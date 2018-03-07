# validate_docker_inputs
Standardized check for docker inputs directory

# Installation instructions:
```git clone https://github.com/justinblaber/validate_docker_inputs.git```

To test out the validator, you must have:
1) An `/INPUTS` folder
2) An `/extra` folder with `inputs.yaml` in it

`inputs.yaml` must be a directory/file structure of the inputs to the docker container, for example:
```
---
root:
- INPUTS:
    - T1.nii.gz // Raw T1 nifti image
```

If the `/INPUTS` directory is empty, the following gets returned along with a non-zero exit code:
```
$ python validate_docker_inputs.py 
This docker has the following INPUTS directory structure: 
\INPUTS
  -T1.nii.gz (Raw T1 nifti image)
```

If the `INPUTS` directory is non-empty but is missing one of the inputs, the following gets returned along with a non-zero exit code:
```
$ python validate_docker_inputs.py 
Incorrect inputs; reason: File does not exist: /INPUTS/T1.nii.gz

This docker has the following INPUTS directory structure: 
\INPUTS
  -T1.nii.gz (Raw T1 nifti image)
```

Lastly, if the inputs are present, then the following gets returned along with a zero exit code:
```
$ python validate_docker_inputs.py 
INPUTS directory is correct!
```
