list_snapshot = {
    'status_code': [200],
    'response_body': {
        'type': 'object',
        'properties': {
            'snapshots': {
                'type': 'array',
                'items': {
                    'type': 'object',
                    'properties': {
                        "chain_id": {'type': 'string'},
                        "created_at": {'type': 'string'},
                        "display_description": {'type': 'string'},
                        "display_name": {'type': 'string'},
                        "instance_uuid": {'type': 'string'},
                        "parent": {'type': ['string', 'null']},
                        "project_id": {'type': 'string'},
                        "size": {'type': 'integer'},
                        "snapshot_id": {'type': 'string'},
                        "user_id": {'type': 'string'},
                    },
                    'additionalProperties': False,
                    'required': ['chain_id', 'instance_uuid', 'project_id', "snapshot_id"]
                }
            },

        },
        'additionalProperties': False,
        'required': ['snapshots']
    }
}
