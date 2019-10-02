from growbox import create_app


def main():
    app, thread, logger = create_app()
    logger.info("Start GrowBox app")
    thread.start()
    app.run(host="0.0.0.0", debug=False, threaded=True)


if __name__ == "__main__":
    main()
