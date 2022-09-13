#!/usr/bin/env python
# coding: utf-8

# In[ ]:


import argparse
import datetime
import requests
import json

import sevenbridges as sbg
from sevenbridges.http.error_handlers import rate_limit_sleeper, maintenance_sleeper

class FHIR2Vis:

    def __init__(self, cavatica_token, cavatica_project_id, fhir_auth_cookie):
        self.cavatica_token = cavatica_token
        self.cavatica_project = cavatica_project_id
        self.fhir_auth_cookie = fhir_auth_cookie
        self.CAVATICA_API_URL="https://cavatica-api.sbgenomics.com/v2"
        self.INCLUDE_FHIR= "https://include-api-fhir-service.includedcc.org/"
                                

    def main(self):
        """Retrieve the metadata from the INCLUDE FHIR Server"""
        
        api = sbg.Api(url=self.CAVATICA_API_URL, token=self.cavatica_token, advance_access=True, 
                        error_handlers=[rate_limit_sleeper, maintenance_sleeper])
        files = api.files.query(project=self.cavatica_project).all()
        start = datetime.datetime.now()
        # print(f"Starting this at: {start}")
        
        # Create empty list
        meta = []
        count = 0
        
        for fh in files:
                        
            document_reference_url = fh.metadata['fhir_document_reference']
            if document_reference_url is None:
                continue
            
            # initial document request
            req_j_total = 0
            req = requests.get(document_reference_url, cookies = {"AWSELBAuthSessionCookie-0" : self.fhir_auth_cookie})
            req_j = req.json()
            if req_j['total'] == 0:
                req_j_total += 1
                continue
            else:
                # Create list of meta data to visualize
                pat = self.get_patient_info(document_reference_url, req_j)
                
                info = [self.get_sample_id(document_reference_url, req_j), 
                        pat['case_id'],
                        pat['type'],
                        pat['gender'],
                        pat['race'],   
                        pat['ethnicity'], 
                        self.get_trisomy_state(document_reference_url, req_j)] 
                meta.append(info)
                
        stop = datetime.datetime.now()
        delta = stop - start
        print(json.dumps(meta))

        
    def get_sample_id(self, document_reference_url, req_j):
#         #req = requests.get(document_reference_url, cookies = {"AWSELBAuthSessionCookie-0" : self.fhir_auth_cookie})
#         #req_j = req.json()
        specimen = req_j['entry'][0]['resource']['context']['related'][0]['reference']
        query = f"{self.INCLUDE_FHIR}{specimen}"
        req2 = requests.get(query, cookies = {"AWSELBAuthSessionCookie-0" : self.fhir_auth_cookie})
        req2_j = req2.json()
        sample_id = ""
        for identifier in req2_j['identifier']:
            if identifier['use'] == "official":
                sample_id = identifier['value']
                break
        return sample_id
        

    def get_patient_info(self, document_reference_url, req_j):
#         req = requests.get(document_reference_url, cookies = {"AWSELBAuthSessionCookie-0" : self.fhir_auth_cookie})
#         req_j = req.json()
        patient_number = req_j['entry'][0]['resource']['subject']['reference']
        query = f"{self.INCLUDE_FHIR}{patient_number}"
        req2 = requests.get(query, cookies = {"AWSELBAuthSessionCookie-0" : self.fhir_auth_cookie})
        req2_j = req2.json()
        pat = {}
        case_id = ""
        for identifier in req2_j['identifier']:
            if identifier['use'] == "official":
                case_id = identifier['value']
                break
        
        dtype = ""
        if 'entry' in req_j.keys() and 'resource' in req_j['entry'][0].keys():
            dtype = req_j['entry'][0]['resource']['type']['coding'][0]['display']
        
        race = ""
        ethnicity = ""
        if "extension" in req2_j.keys():
            for ext in req2_j['extension']:
                if ext['url'] == "http://hl7.org/fhir/us/core/StructureDefinition/us-core-race":
                    race = ext['extension'][-1]['valueString']
                elif ext['url'] == "http://hl7.org/fhir/us/core/StructureDefinition/us-core-ethnicity":
                    ethnicity = ext['extension'][-1]['valueString']
            
        pat['case_id'] = case_id
        pat['type'] = dtype
        pat['gender'] = req2_j['gender']
        pat['race'] = race
        pat['ethnicity'] = ethnicity
        return pat
        
        
    def get_trisomy_state(self, document_reference_url, req_j):
#         #req = requests.get(document_reference_url, cookies = {"AWSELBAuthSessionCookie-0" : self.fhir_auth_cookie})
#         #req_j = req.json()
        
        patient_number = req_j['entry'][0]['resource']['subject']['reference']

        # Check if trosomy is present and confirmed
        # Condition --> `MONDO:000860`
        # verification-status=confirmed
        # patient/<number>
        # 
        # all url escaped looks like:
        # Condition?code=MONDO%3A0008608&subject=Patient%2F4927&verification-status=confirmed&_format=json

        query = f"{self.INCLUDE_FHIR}Condition?code=MONDO:0008608&verification-status=confirmed&subject={patient_number}&_format=json"
#         print(query)
        req2 = requests.get(query, cookies = {"AWSELBAuthSessionCookie-0" : self.fhir_auth_cookie})
        
        req2_j = req2.json()
        total = req2_j['total']
        trisomy_state = ""
        if total == 0:
            trisomy_state = "D21"
        elif total == 1:
            trisomy_state = "T21"
        return trisomy_state
    
    
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Retrieve metadata from the INCLUDE Server and updates the metadata on the Cavatica Project')
    parser.add_argument("--cavatica_token", required=True, help="You can find your developer token at https://cavatica.sbgenomics.com/developer/token")
    parser.add_argument("--cavatica_project", required=True, help="The Cavatica project where the files are already imported from the INCLUDE Portal")
    parser.add_argument("--include_fhir_authentication_cookie", required=True, 
                        help="The Authorization cookie from the INCLUDE FHIR Server (https://include-api-fhir-service.includedcc.org/) \
                            To obtain the cookie, open the Chorme or Firefox console, go to the Application tab and copy the value \
                            contained in `AWSELBAuthSessionCookie-0`.")
    args = parser.parse_args()
    fhir2vis = FHIR2Vis(args.cavatica_token, args.cavatica_project, args.include_fhir_authentication_cookie)
    fhir2vis.main()

