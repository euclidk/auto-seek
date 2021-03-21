import time
import requests
import requests_cache
import random

requests_cache.install_cache()
import json

PREFERENCES = {
    "keywords": "Graduate Electrical Engineer",
    "where": "Perth"
}

HRULE = "-" * 100

seekUrl = "https://www.seek.com.au/"

def timer(func):
    def wrapper():
        start = time.time()
        func()
        print(f'Took {time.time() - start} seconds to complete.')

    return wrapper

@timer
def main():
        # Saves a json file with all the unique employer questions. Fill out with myAnswer

        # {
        #     "1": {
        #         "answerType": "singleSelect",
        #         "myAnswer": null,
        #         "options": [
        #             "Yes",
        #             "No"
        #         ],
        #         "text": "Do you have a current Australian driver's licence?"
        #     },
        #     "10": {
        #         "answerType": "singleSelect",
        #         "myAnswer": null,
        #         "options": [
        #             "Completed Year 9 - 11",
        #             "Completed High School (Year 12)",
        #             "Certificate I",
        #             "Certificate II",
        #             "Certificate III",
        #             "Certificate IV",
        #             "Diploma",
        #             "Advanced Diploma",
        #             "Associate Degree",
        #             "Bachelor Degree",
        #             "Bachelor Degree (Honours)",
        #             "Graduate Certificate",
        #             "Graduate Diploma",
        #             "Masters Degree",
        #             "Doctoral Degree"
        #         ],
        #         "text": "What's your highest level of education?"
        #     }, ...
        # }

    pgnum = 1

    Questionnaire = {}
    easyLinks = []

    while pgnum < 10:

        pgJson = requests.get(f"{seekUrl}api/chalice-search/search?", params=dict(PREFERENCES, **{"page":pgnum})).json()
        print(f"{HRULE}\nPage number: {pgnum}\n{HRULE}")

        for job in pgJson['data']:

            jobJson = requests.get(f"https://ca-jobapply-ex-api.cloud.seek.com.au/jobs/{job['id']}").json()
            print(f"{job['advertiser']['description']:50} {job['title']:80} {job['area']:30} {seekUrl}job/{job['id']:<12} {not jobJson['isLinkOut']}")

            if jobJson['questionnaire']:
                for q in jobJson['questionnaire']['questions']:
                    Questionnaire.update({
                        q['id']: q
                    })

                    qtype = Questionnaire[q['id']]['answerType']

                    if qtype == 'singleSelect':
                        Questionnaire[q['id']].update({"myAnswer": random.randint(0, len(Questionnaire[q['id']]['options'])-1)})
                    elif qtype == 'multiSelect':
                        Questionnaire[q['id']].update({"myAnswer": [random.randint(0, len(Questionnaire[q['id']]['options'])-1)]})
                    elif qtype == 'freeText':
                        Questionnaire[q['id']].update({"myAnswer": "This is my free text response."})
                    Questionnaire[q['id']].pop("id")

            elif jobJson['isLinkOut'] == False:
                easyLinks.append(job['id'])

        pgnum += 1

    with open('questionnaire.json', 'w') as f:
        f.write(json.dumps(Questionnaire, sort_keys=True, indent=4))

    print(f"{HRULE}\nHere are the job id's that are easy to apply:\n{HRULE}")
    for e in easyLinks:
        print(e, end=', ')
        with open('easyApplyLinks.csv', 'a') as f:
            f.write(f"{e}, ")
    print(f"\n{HRULE}\nHere is the list of unique employer questions\n{HRULE}")
    for k in Questionnaire.keys():
        print(Questionnaire[k]['text'])
    print(f"{len(Questionnaire)} unique questions found.")

    return True

if __name__ == "__main__":
    main()