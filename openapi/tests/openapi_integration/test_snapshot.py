from time import sleep
import pytest

from .helpers.helpers import request_with_validation
from .helpers.collection_setup import basic_collection_setup, drop_collection

collection_name = 'test_collection_snapshot'


@pytest.fixture(autouse=True)
def setup():
    basic_collection_setup(collection_name=collection_name)
    yield
    drop_collection(collection_name=collection_name)


def test_snapshot_operations():
    # no snapshot on collection
    response = request_with_validation(
        api='/collections/{collection_name}/snapshots',
        method="GET",
        path_params={'collection_name': collection_name},
    )
    assert response.ok
    assert len(response.json()['result']) == 0

    # create snapshot on collection
    response = request_with_validation(
        api='/collections/{collection_name}/snapshots',
        method="POST",
        path_params={'collection_name': collection_name},
        query_params={'wait': 'true'},
    )
    assert response.ok
    snapshot_name = response.json()['result']['name']

    # validate it exists
    response = request_with_validation(
        api='/collections/{collection_name}/snapshots',
        method="GET",
        path_params={'collection_name': collection_name},
    )
    assert response.ok
    assert len(response.json()['result']) == 1
    assert response.json()['result'][0]['name'] == snapshot_name

    # delete it
    response = request_with_validation(
        api='/collections/{collection_name}/snapshots/{snapshot_name}',
        method="DELETE",
        path_params={'collection_name': collection_name,
                     'snapshot_name': snapshot_name},
        query_params={'wait': 'true'},
    )
    assert response.ok

    # validate it is gone
    response = request_with_validation(
        api='/collections/{collection_name}/snapshots',
        method="GET",
        path_params={'collection_name': collection_name},
    )
    assert response.ok
    assert len(response.json()['result']) == 0

    # no full snapshot
    response = request_with_validation(
        api='/snapshots',
        method="GET",
    )
    assert response.ok
    assert len(response.json()['result']) == 0

    # create full snapshot
    response = request_with_validation(
        api='/snapshots',
        method="POST",
    )
    assert response.ok
    snapshot_name = response.json()['result']['name']

    # validate it exists
    response = request_with_validation(
        api='/snapshots',
        method="GET",
    )
    assert response.ok
    assert len(response.json()['result']) == 1
    assert response.json()['result'][0]['name'] == snapshot_name

    # delete it
    response = request_with_validation(
        api='/snapshots/{snapshot_name}',
        path_params={'snapshot_name': snapshot_name},
        method="DELETE",
        query_params={'wait': 'true'},
    )
    assert response.ok

    response = request_with_validation(
        api='/snapshots',
        method="GET",
    )
    assert response.ok
    assert len(response.json()['result']) == 0

@pytest.mark.timeout(180)
def test_snapshot_operations_non_wait():
    # there no snapshot on collection
    response = request_with_validation(
        api='/collections/{collection_name}/snapshots',
        method="GET",
        path_params={'collection_name': collection_name},
    )
    assert response.ok
    assert len(response.json()['result']) == 0

    # create snapshot on collection
    response = request_with_validation(
        api='/collections/{collection_name}/snapshots',
        method="POST",
        path_params={'collection_name': collection_name},
        query_params={'wait': 'false'},
    )
    assert response.status_code == 202
    
    # validate it exists
    snapshot_name = None
    while True:
        try:
            response = request_with_validation(
                api='/collections/{collection_name}/snapshots',
                method="GET",
                path_params={'collection_name': collection_name},
            )
            assert response.ok
            assert len(response.json()['result']) == 1
            snapshot_name = response.json()['result'][0]['name']
            break
        except AssertionError:
            # wait for snapshot to be created
            sleep(0.1)
            continue
        
    # delete it
    response = request_with_validation(
        api='/collections/{collection_name}/snapshots/{snapshot_name}',
        method="DELETE",
        path_params={'collection_name': collection_name,
                     'snapshot_name': snapshot_name},
        query_params={'wait': 'false'},
    )
    assert response.status_code == 202

    # validate it is gone
    while True:
        try:
            response = request_with_validation(
                api='/collections/{collection_name}/snapshots',
                method="GET",
                path_params={'collection_name': collection_name},
            )
            assert response.ok
            assert len(response.json()['result']) == 0
            break
        except AssertionError:
            # wait for snapshot to be deleted
            sleep(0.1)
            continue
        
    # no full snapshot
    response = request_with_validation(
        api='/snapshots',
        method="GET",
    )
    assert response.ok
    assert len(response.json()['result']) == 0

    # create full snapshot
    response = request_with_validation(
        api='/snapshots',
        method="POST",
        query_params={'wait': 'false'},
    )
    assert response.status_code == 202

    # validate it exists
    while True:
        try: 
            response = request_with_validation(
                api='/snapshots',
                method="GET",
            )
            assert response.ok
            assert len(response.json()['result']) == 1
            snapshot_name = response.json()['result'][0]['name']
            break
        except AssertionError:
            # wait for snapshot to be created
            sleep(0.1)
            continue
        
    # delete it
    response = request_with_validation(
        api='/snapshots/{snapshot_name}',
        path_params={'snapshot_name': snapshot_name},
        method="DELETE",
        query_params={'wait': 'false'},
    )
    assert response.status_code == 202

    while True:
        try:    
            response = request_with_validation(
                api='/snapshots',
                method="GET",
            )
            assert response.ok
            assert len(response.json()['result']) == 0
            break
        except AssertionError:
            # wait for snapshot to be deleted
            sleep(0.1)
            continue