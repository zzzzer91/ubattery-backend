from ubattery import create_app, socketio


socketio.run(create_app())