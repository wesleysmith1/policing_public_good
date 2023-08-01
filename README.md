this project is cloned from delegated_pubishmen2 project. 

because both projects are owned by same user a fork was not possible

the following command was run to set upstream after cloning delegated_punishment2

'''
git remote add upstream https://github.com/wesleysmith1/delegated_pubishmen2.git
'''

to pull changes from delegated_punishment2 run the following

''' 
git checkout main
git pull upstream main
git push origin main
'''

Now merge the code into the feature branch. In this case the feature branch is just the main branch for policing_public_good and is named policing-public-good.

'''
git checkout policing_public_good
git merge main
'''