
# COVID-19 Challenge

### Root

|── README.md

|── environment_setup.sh

|── conver_testformat.py

|── nnunet

|── nnUNet_raw_data_base ([download](https://drive.google.com/drive/folders/194hHX5cOFoPi0VvIKNMoAIqHppG1YwWI?usp=sharing))

|── nnUNet_preprocessed ([download](https://drive.google.com/drive/folders/1bcpLwVSd_QFEm_GLR0a2RddIqa4RIC-M?usp=sharing))

|── nnUNet_trained_models (If you train the model, it will be made automatically)



### Setting Environment

```
# ./environment_setup.sh
```



### Training

```bash
CUDA_VISIBLE_DEVICES=1 python nnunet/run/run_training.py 3d_fullres nnUNetTrainerV2 Task000_MYTASK -f 0
```



### Inference

```bash
CUDA_VISIBLE_DEVICES=1 python nnunet/inference/predict_simple.py -i nnUNet_raw_data_base/nnUNet_raw_data/Task000_MYTASK/imagesTs -o '$output_path' -t Task000_MYTASK -m 3d_fullres -f 0
```



### Convert Data (for submission)

If you finished the inference, you can check a new folder named $output_path

```bash
python convert_testformat.py --data_path='$output_path'
```



Then, you can find submission folder in your '$output_path'.

please compress it and submit.