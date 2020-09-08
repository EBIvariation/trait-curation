# Instructions to deploy the app in the EBI Embassy Cloud

[Link to the Embassy Cloud documentation](http://docs.embassy.ebi.ac.uk/)

## Initial Embassy set up
1. Request the tenancy through the Resource Usage Portal. See docs on the EBI intranet for details.
1. Once accepted, generate the Embassy admin password as described in the email.
1. Log in to the OpenStack dashboard. URL is also provided in the email.

## Set up keys and network interfaces
1. **Key pairs.**
    * Go to Compute → Access & Security → Key Pairs.
    * Click on “Import Key Pair” and add public SSH keys for every collaborator who will need to have SSH access to the instances.
1. **Floating IPs.**
    * Go to Compute → Access & Security → Floating IPs
    * Create the necessary number of floating IPs (one for each instance you would like to make publicly accessibly). Use the external network which you identified on the previous step.
1. **Security group.**
    * Go to Compute → Access & Security → Security Groups.
    * Click on “Create Security Group”. Name = “Web app”, description = “Allows inbound SSH and ICMP access. Opens ports 80, 443, and 8000.”.
    * Click on “Manage rules” for that security group.
    * Add the rules for: “SSH”, “ALL ICMP”, “HTTP”, “HTTPS”, and “Custom TCP Rule” with Port=8000.

## Create and set up the instances
1. Go to Compute → Instances and click on “Launch Instance”. Set the parameters:
    * **Instance Name** = `trait-curation` (of anything else)
    * **Count** = 2 (or however many you need). If you choose more than one, a numeric suffix will be appended to the instance name, e.g. `trait-curation-1`, `trait-curation-2`, etc.
    * **Source** = `Ubuntu18.04LTS`
    * **Flavor** = `s1.large` (4 VCPUs, 8 GB RAM, 60 GB total disk)
    * **Networks** = add the default one (created with the project)
    * **Security Groups** = use the “SSH-and-ping” one created during the set up stage.
    * **Key Pair** = choose the key pair of **one** of the collaborators who will need to have access to the instance. Only one key pair can be chosen at this stage.
1. For each of the instances, click Actions → Associate floating IP.

## SSH into an instance and set up
Use the command: `ssh ubuntu@${FLOATING_IP}`, substituting the actual floating IP of the instance you're trying to get into.

Configure SSH access for other collaborators by adding their public keys into `~/.ssh/authorized_keys`. They will also need to use the `ubuntu` user, which has root privileges.
