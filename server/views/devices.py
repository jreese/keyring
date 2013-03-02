from flask import abort, flash, g, redirect, request
from sqlalchemy.exc import IntegrityError

from core import app, authenticate, db, sessions, api, context, get, post, template
from models import Device

with context('/devices'):

    @api('', methods=['GET'])
    @authenticate
    def api_devices_list(method):
        """List all registered devices for the current user."""
        return Device.load_by_user(g.user.id)

    @api('/register', methods=['POST'])
    @authenticate
    def api_devices_register(method, payload):
        """Register a new device."""

        if 'name' in payload:
            try:
                device = Device(g.user, payload['name'])
                if 'push_id' in payload:
                    device.push_id = payload['push_id']

                db.add(device)
                db.commit()

                return {
                    'api_key': device.api_key,
                    'device': device,
                }
            except IntegrityError:
                abort(400, 'Device name already exists')

        abort(400, 'Missing payload parameters')

with context('/device'):

    @api('/<id>', methods=['GET','POST','DELETE'])
    @authenticate
    def api_device(method, id, payload=None):
        """Retrieve device info, update its attributes, or delete a device for
        the current user."""
        device = Device.load(id)
        app.logger.debug(device)
        if (device is None or
            device.uid != g.user.id
           ):
            abort(404)

        if method == 'GET':
            return device

        elif method == 'POST':
            if 'name' in payload:
                device.name = payload['name']
            if 'push_id' in payload:
                device.push_id = payload['push_id']

            try:
                db.add(device)
                db.commit()
            except IntegrityError:
                abort(400, 'Device name already exists')

            return device

        elif method == 'DELETE':
            db.delete(device)
            db.commit()
            return True

