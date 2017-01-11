# MixPlayer
Google Cloud Platform based Mix Player

## Setup
This project is a simple application for posting music mixes. I haven't checked in any supporting code. Here's how 
I make this project in Eclipse and PyDev. It took a bit of messing with. Here's what I wanted: 

1. Use Google App Engine and Google Cloud Storage. I don't want to host *anything*.
1. Use virtualenv to avoid dependency problems with Python libraries. 
1. Use Eclipse and PyDev. PyDev was a pain point. 

Zero hosting. Getting something to work is enjoyable. Maintaining it is not. I like platform as a service because 
I can make my program work and maintain that. I don't have to keep a Linux system secure. 

Speaking of Linux... it's my jam. Ubuntu makes heavy use of Pyhon for system tasks. I don't want to mess with any 
system libraries using pip. Besides, anything I install with pip will have to be [vendored](https://cloud.google.com/appengine/docs/python/tools/using-libraries-python-27)
into App Engine anyway so why worry about it? I want virtualenv so that I can have control over what packages 
I'm using. 

I like having modern tools. Much of my Python development happens in Emacs. It's perfect for system automation tasks. 
Web projects need complex frameworks and lots of API code. It's way easier to program with auto completion, code 
refactoring, etc. Since I'm already used to the cruelty and pain of using Eclipse I thought I'd do PyDev. 

I'm using Ubuntu 14.04. I'd rather use 16.04 but I'm stuck because of the NASA Swarmathon. 

### Step 0: Setup Eclipse Neon 

You need Java 8 for it. There's a PPA with Java 8 support for Ubuntu. I pray that it stays alive. 

### Step 1: Setup my Python Environment 

I use virtualenv to setup the system's Python 2.7 interpreter. That's the version preferred by App Engine:

```shell
mkdir -p ~/Mix 
virtualenv -p /usr/bin/python ~/Mix/env
source ~/Mix/env/bin/activate
```

### Step 2: Create the Eclipse Project 

You need to install Eclipse and PyDev. You also need to install the [Google Cloud Platform SDK for Python](https://cloud.google.com/sdk/docs/).
When you create the project have Eclipse put source in the project root. If you don't put the *.yaml file there the
launches will fail.

### Step 2: Install APIs

This was painful (and cost me four hours) because PyDev doesn't support namespace packages in Python which is how 
Google distributes some APIs. No use filing a bug. They've had [six years](https://sourceforge.net/p/pydev/bugs/1305/) 
to work on it. The problem is that PyDev sees imports as broken because it doesn't understand how they are packaged
and though the program works you get error markers and no code completion. See number 3 above. 

The workaround is to install some packages using pip and some using *both* pip and easy_install. Here's what it took:

```shell
mkdir ~/Mix/Project/lib 
pip install -t ~/Mix/Project/lib --upgrade google-api-python-client
```

To be continued...
