Python AWS CDK solution for setup sync and datalake for DSB
========

This is Python CDK project to create a datalake and set of Lambdas for automatic sync and analyse data provided by DSB app of heinekingmedia.

## How it Works

This project uses a simple structure for sources, tooling and testing.
Just execute `make` to see what you can do.

**Current status:** Under development

## How to start

You will need to have Python 3.9 installed.
The `install_venv.sh` helper script creates a virtualenv within this
project, stored under the `.venv` directory.
It needs to be executed in the process of the terminal as following
 ```
 $ source ./install_venv.sh
 ```

 After this you just need to call
 ```
 $ make install
 ```
This will also install AWS cdk command by calling `npm install -g aws-cdk`.

### Python

To create the virtualenv it assumes that there is a `python3`
(or `python` for Windows) executable in your path with access to the `venv`
package. If for any reason the automatic creation of the virtualenv fails,
you can create the virtualenv manually.

You can use `source ./install_venv.sh` to create Python environment
for this project on MacOS and Linux:

If you are a Windows platform, you would need to install and activate the virtualenv like this:

```
% python3 -m venv .venv
% .venv\Scripts\activate.bat
```

To add additional dependencies, for example other CDK libraries, just add
them to your `requirements.txt` file. Please rerun `make install` after changing it.

It is tested with Python 3.9.x.

### PyTest

Project uses PyTest for a simple testing approach.
For reference visit: https://docs.pytest.org/en/latest/index.html

### AWS CDK

If you use profiles for AWS CLI, you will need to set `--profile`parameter in every following cdk command.

For reference on AWS CDK visit: https://docs.aws.amazon.com/de_de/cdk

If you never used CDK with the target AWS account and region, you need to
bootstrap it.
```
$ cdk bootstrap
```

At this point you can now synthesize the CloudFormation template for this code.
```
$ cdk synth
```

After this, use deploy command to deploy CloudFormation stack.
```
cdk deploy
```

The `cdk.json` file tells the CDK Toolkit how to execute your app.
For reference on AWS CDK visit: https://docs.aws.amazon.com/de_de/cdk

### Useful CDK commands

 * `cdk ls`          list all stacks in the app
 * `cdk synth`       emits the synthesized CloudFormation template
 * `cdk deploy`      deploy this stack to your default AWS account/region
 * `cdk diff`        compare deployed stack with current state
 * `cdk docs`        open CDK documentation

Enjoy!

## Prerequisites

* **Python 3.9.x** for CDK code and AWS Lambda implementation
* **NodeJS** and npm for cli commands for CDK and
* **Docker** to build AWS Lambda archive locally with CDK
* **AWS CDK 2.x** for everything

### Local development

This is developed to support development under Mac OS X, Windows and Linux (Ubuntu, CentOS).
For local testing you will need to install Python 3.9.x.

## License

This project is licensed under the terms of the MIT license.
