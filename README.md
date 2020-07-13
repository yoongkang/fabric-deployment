# Basic fabric deployment script

## Background

Since 2018, there has been a new version of `fabric` which is compatible with Python 3. It's also called `fabric2`.

This change came with an updated API, and is thus incompatible with old fabric 1.x fabfiles.

There isn't much information online on how to do a proper deployment, and the official documentation appears to be a bit sparse.

Thus, I decided to post the `fabfile` I'm using for deploying Python web application. Specifically I deal with Django applications, but you should be able to use this with any Python framework.

The idea is to `rsync` a repository to a directory in your remote server, but you can modify this to use any command, e.g `git pull`.

## Requirements

You need to install `fabric` and `patchwork`. The most recent versions should work, but I have included a `requirements.txt` in case you need the exact versions I'm using, for some reason.

## Configuration

I've used environment variables to configure things like the username for the remote server, the target directory, etc.

Feel free to modify those as you wish, they're near the top `fabfile.py`.

I'm also using `pipenv` for package management on my servers, but if you don't use this, you can modify the commands yourself.

## Usage

Run the following command:

```
usage: fab deploy [--no-migrate] [--no-dependencies] [--collectstatic]

options:

  --no-migrate         Skips migration
  --no-dependencies    Skips installing dependencies
  --collectstatic      Runs collectstatic
```

By default, it will run migrations and install dependencies, but not run `collectstatic`.

If you want to change that behaviour, change the `deploy()` task.

