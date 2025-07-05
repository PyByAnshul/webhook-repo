from flask import Blueprint, request, jsonify
from app.extensions import mongo
from datetime import datetime
import logging

webhook = Blueprint('Webhook', __name__, url_prefix='/webhook')


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def readable_time(iso_timestamp: str) -> str:
    try:
        utc_time = datetime.fromisoformat(iso_timestamp.replace('Z', '+00:00'))

        day = utc_time.day
        if 11 <= day <= 13:
            suffix = 'th'
        else:
            suffix = {1: 'st', 2: 'nd', 3: 'rd'}.get(day % 10, 'th')

        return utc_time.strftime(f"{day}{suffix} %B %Y - %I:%M %p UTC")

    except Exception as error:
        logger.error(f"Could not convert timestamp: {error}")
        return iso_timestamp



def handle_push_event(data):
    try:
        branch = data.get('ref', '').replace('refs/heads/', '')
        commits = data.get('commits', [])
        author = commits[0]['author']['name'] if commits else data.get('pusher', {}).get('name', 'Unknown')
        timestamp = readable_time(data.get('head_commit', {}).get('timestamp', ''))
        request_id = data.get('head_commit', {}).get('id', '')

        return {
            'request_id': request_id,
            'author': author,
            'from_branch': '',
            'to_branch': branch,
            'timestamp': timestamp
        }
    except Exception as err:
        logger.error(f"Push event error: {err}")
        return None


def handle_pull_request_event(data):
    try:
        pr = data.get('pull_request', {})
        action = data.get('action')

        if action not in ['opened', 'reopened']:
            return None

        author = pr.get('user', {}).get('login', 'Unknown')
        from_branch = pr.get('head', {}).get('ref', 'Unknown')
        to_branch = pr.get('base', {}).get('ref', 'Unknown')
        timestamp = readable_time(pr.get('created_at', ''))
        request_id = pr.get('head', {}).get('sha', '')

        return {
            'request_id': request_id,
            'author': author,
            'from_branch': from_branch,
            'to_branch': to_branch,
            'timestamp': timestamp
        }
    except Exception as err:
        logger.error(f"Pull request event error: {err}")
        return None


def handle_merge_event(data):
    try:
        pr = data.get('pull_request', {})
        if data.get('action') != 'closed' or not pr.get('merged'):
            return None

        author = pr.get('merged_by', {}).get('login', 'Unknown')
        from_branch = pr.get('head', {}).get('ref', 'Unknown')
        to_branch = pr.get('base', {}).get('ref', 'Unknown')
        timestamp = readable_time(pr.get('merged_at', ''))
        request_id = pr.get('head', {}).get('sha', '')

        return {
            'request_id': request_id,
            'author': author,
            'from_branch': from_branch,
            'to_branch': to_branch,
            'timestamp': timestamp
        }
    except Exception as err:
        logger.error(f"Merge event error: {err}")
        return None


@webhook.route('/receiver', methods=["POST"])
def receive_webhook():
    try:
        event_type = request.headers.get('X-GitHub-Event', '')
        data = request.get_json()

        logger.info(f"Received GitHub event: {event_type}")
        result = None

        if event_type == 'push':
            result = handle_push_event(data)
        elif event_type == 'pull_request':
            result = handle_pull_request_event(data) or handle_merge_event(data)

        if result:
            inserted = mongo.db.github_events.insert_one(result)
            logger.info(f"Event saved to DB with ID: {inserted.inserted_id}")

            return jsonify({
                'status': 'success',
                'message': 'Event processed and stored',
                'event_id': str(inserted.inserted_id)
            }), 200

        logger.info(f"No handler for event: {event_type}")
        return jsonify({'status': 'ignored', 'message': f"{event_type} not handled"}), 200

    except Exception as err:
        logger.error(f"Webhook processing error: {err}")
        return jsonify({'status': 'error', 'message': str(err)}), 500


@webhook.route('/events', methods=["GET"])
def list_events():
    try:
        events = list(mongo.db.github_events.find(
            {}, {'_id': 0}
        ).sort('timestamp', -1))

        return jsonify({'status': 'success', 'events': events}), 200
    except Exception as err:
        logger.error(f"Failed to fetch events: {err}")
        return jsonify({'status': 'error', 'message': str(err)}), 500


@webhook.route('/health', methods=["GET"])
def health():
    return jsonify({'status': 'healthy', 'message': 'Webhook service is running'}), 200
