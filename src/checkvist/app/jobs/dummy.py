"""
Dummy job.
"""
import logging
from checkvist.lib import Task

log = logging.getLogger(__name__)


def main(task: Task):
    try:
        log.info(f'Task received: {task}')
        log.info('Returning None. Task won\'t be modified.')
        return None
    except Exception as e:
        log.error(f"Error running job 'dummy' over {task}: {e}")
