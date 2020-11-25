from typing import Union, Optional, List, Dict
from importlib import import_module
from pathlib import Path
import logging
import os

from checkvist.lib import Checklist, Task
from checkvist import Client

log = logging.getLogger(__name__)

JOBS_DIR = Path(__file__).parent.joinpath('jobs')


class Job:
    def __init__(self, job: Union[str, Path]):
        if isinstance(job, str):
            self.file = job.replace('-', '_')
        elif isinstance(job, Path):
            self.file = job.stem
        self._module = None

    @property
    def module(self):
        if self._module is None:
            qual = f'checkvist.app.jobs.{self.file}'
            self._module = import_module(qual)
        return self._module

    @property
    def doc(self):
        return (self.module.__doc__ or '').strip()

    def __call__(self, task: Task):
        return self.module.main(task)

    def __repr__(self):
        return f'Job({self.__str__()})'

    def __str__(self):
        return self.file.replace('_', '-')


class App:
    def __init__(
        self,
        username: Optional[str] = None,
        secret: Optional[str] = None,
    ):
        self.username = username or os.getenv('CHECKVIST_USERNAME')
        self.secret = secret or os.getenv('CHECKVIST_SECRET')
        self._jobs = None

    @property
    def client(self):
        if getattr(self, '_client', None) is None:
            self._client = Client(self.username, self.secret)
        return self._client

    @property
    def lists(self) -> List[Checklist]:
        if getattr(self, '_lists', None) is None:
            self._lists = self.client.get_lists()
        return self._lists

    @property
    def jobs(self) -> Dict[str, Job]:
        if getattr(self, '_jobs', None) is None:
            self._jobs = {str(j): j for j in self._get_jobs()}
        return self._jobs

    def find_lists(self, *lists: Union[str, int]) -> List[Checklist]:
        checklists = list()
        found = list()

        for l in lists:
            if isinstance(l, int) or l.isnumeric():
                res = [x for x in self.lists
                       if x.id == int(l) or x.name == str(l)]
            else:
                res = [x for x in self.lists if x.name == l]

            if res:
                checklists.extend(res)
                found.append(l)

        notfound = [l for l in lists if l not in found]
        if notfound:
            raise ValueError(f'Checklists not found: {", ".join(notfound)}')

        return checklists

    def import_jobs(self, *jobs: str):
        modules = list()

        for job in jobs:
            try:
                modules.append(self.jobs[job])
            except KeyError:
                raise ValueError(f"Job '{job}' not found")

        return modules

    def _get_jobs(self):
        jobs = list()

        for file in JOBS_DIR.iterdir():
            job = Job(file)
            try:
                job.doc
            except Exception as e:
                log.error(f"Error importing job '{job}': {e}")
            else:
                jobs.append(job)

        return jobs

    def run_jobs(
        self,
        jobs:  List[str],
        lists: Optional[Union[str, int]] = None
    ):
        checklists = self.find_lists(*lists) if lists else self.lists
        jobs = self.import_jobs(*jobs)

        for checklist in checklists:
            log.info(f"Retrieving tasks from checklist {checklist.id} "
                     f"'{checklist.name}' ({checklist.item_count})")

            for task in self.client.get_tasks(list_id=checklist.id):
                modified = False

                for job in jobs:
                    log.info(f"Running job '{job}' over task {task.id}")
                    try:
                        content = job(task)
                        if content is not None:
                            task.content = content
                            modified = True
                    except Exception as e:
                        log.error(f"Error running '{job}' over {task}: {e}")

                if modified:
                    self.client.update_task(list_id=checklist.id,
                                            task_id=task.id,
                                            content=task.content)

    def show_user_info(self) -> str:
        info = self.client.get_user_info()
        return '\n'.join(f'{k}: {v}' for k, v in info.items())
