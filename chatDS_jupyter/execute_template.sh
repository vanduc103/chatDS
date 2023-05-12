#!/bin/bash

jupyter nbextension disable chatDS_jupyter/main
jupyter nbextension uninstall chatDS_jupyter
jupyter contrib nbextensions install --sys-prefix --skip-running-check
jupyter nbextension install ./chatDS_jupyter --nbextensions /home/alexbui/anaconda3/lib/python3.9/site-packages/jupyter_contrib_nbextensions/nbextensions
jupyter nbextension enable chatDS_jupyter/main