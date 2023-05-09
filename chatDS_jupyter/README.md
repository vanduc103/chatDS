# planet_jupyter
Sample Jupyter Notebook Extension created for the [Creating a Jupyter Notebook Extension — Part 1](https://medium.com/@aneesha/creating-a-jupyter-notebook-extension-part-1-31c72032cad) blog post.

## Instructions
The instructions below will allow you to setup your development environment to create an extension and continue to edit the code for the extension.

$ conda create --name jupyterexperiments python=3.7
$ conda activate jupyterexperiments
$ conda install -c conda-forge jupyter_contrib_nbextensions
$ pip show jupyter_contrib_nbextensions

Copy code into this folder and can edit from here!
eg /Users/username/anaconda3/envs/jupyterexperiments/lib/python3.7/site-packages/jupyter_contrib_nbextensions/nbextensions

$ cd to nbextensions
$ jupyter contrib nbextensions install --sys-prefix --skip-running-check
$ jupyter nbextension install chatDS_jupyter --nbextensions ./

$ jupyter nbextension enable chatDS_jupyter/main
