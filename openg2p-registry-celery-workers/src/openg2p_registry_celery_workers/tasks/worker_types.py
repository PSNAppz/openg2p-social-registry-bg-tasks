from enum import Enum


class WorkerTypes(str, Enum):
    EXAMPLE_WORKER = "example_worker"
    ID_GENERATION_REQUEST_WORKER = "id_generation_request_worker"
    ID_GENERATION_UPDATE_WORKER = "id_generation_update_worker"
