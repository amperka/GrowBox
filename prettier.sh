#!/bin/bash
prettier --single-quote --trailing-comma es5 --write static/js/'{,/**/}*.js'
prettier --write templates/'{,/**/}*.html'
prettier --write static/css/'{,/**}*.css'
