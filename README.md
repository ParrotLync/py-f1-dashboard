# py-f1-dashboard
Formula1 data dashboard written in Python &amp; Flask. Made for a school project.

### Dataset
Kaggle dataset: 
https://www.kaggle.com/datasets/rohanrao/formula-1-world-championship-1950-2020


### Applicatie gebruiken
- Live version: https://f1predictions.ipictserver.nl/
- Build docker image: (`docker build -t f1predictions .`)
- Use docker-compose: `docker-compose up`
- Manually run flask app (entrypoint `/src/main.py`), install `requirements.txt`
- Use pre-built container image at https://github.com/ParrotLync/py-f1-dashboard/pkgs/container/py-f1-dashboard