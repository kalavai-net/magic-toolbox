# Kalavai Magic Toolbox

## Overview

This repo is the management and deployment API for the Kalavai Magic Toolbox Offering

It primerily wraps and co-ordinates these three Packages and APIS:

1. Model Library -> Defines the core Magic Toolbox Model Cards
2. Kube Watcher -> Used to interact with kubernetes.
3. Tool Library -> Used to interface with Tool Library Deployments.


# TODO:
1. Add gitlab isntalls to the pytoml
1. Use labels in the  selectors for deployments in kw

# BUGS:
1. Delete doesnt get rid of the services (test-service) but does delete (test-) this is because the things associated with the deployment were called $deployment_name-pvc, $deployment_name-storage, $deployment_name-service. So what is the best way of deleting all of the things to do with a deployment?

2. Create returns False, same issue, returs false if teh namespace already exists, even if everything else deployes fine. (fix in kube watcher)

3. Delete returns False if there are any issues, even if it deleted everything, but couldn't find one thing. How do we best deal with these cases. (fix in kube watcher)

# Routes
1. Delete a MT for a User (KW)
2. List all the MTs of a User (KW)
3. Create a new MT for a User (ML + KW)

## TODO
4. Add new servive by URL per Instance + User
5. Remove a service by ID
6. Edit a Tool or set of tools descriptions.

7. Generate ChatGPT Dynamic Config
8. Generate ChatGPT Static Configs

9. Deploy a Kalavai Tool

10. Search for Rapid API Tools.







