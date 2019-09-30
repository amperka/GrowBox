from growbox import app, gb

gb.arduino_thread.start()
gb.logger.info("Server started")
app.run(host="0.0.0.0", debug=False, threaded=True)
