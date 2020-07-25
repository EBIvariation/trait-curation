# Instructions to deploy the app in the EBI Embassy Cloud

## Initial Embassy set up
1. Request the tenancy through the Resource Usage Portal. See docs on the EBI intranet for details.
1. Once accepted, generate the Embassy admin password as described in the email.
1. Log in to the OpenStack dashboard. URL is also provided in the email.

## Set up keys and network interfaces
1. Go to Compute → Access & Security → Key Pairs. Click on “Import Key Pair” and add public SSH keys for every collaborator who will need to have SSH access to the instances.
1. Go to Compute → Access & Security → Floating IPs and create the necessary number of floating IPs (one for each instance you would like to make publicly accessibly). Choose the external network which you identified on the previous step.

## Create and set up the instances
1. Go to Compute → Instances and click on “Launch Instance”. Set the parameters:
    * **Instance Name** = `trait-curation` (of anything else)
    * **Count** = 2 (or however many you need). If you choose more than one, a numeric suffix will be appended to the instance name, e.g. `trait-curation-1`, `trait-curation-2`, etc.
    * **Source** = `Ubuntu18.04LTS`
    * **Flavor** = `s1.large` (4 VCPUs, 8 GB RAM, 60 GB total disk)
    * **Networks** = add the default one (created with the project)
    * **Security Groups** = add the default one
    * **Key Pair** = choose the key pairs of collaborators who will need to have access
1. For each of the instances, click Actions → Associate floating IP.
