import pdfplumber
import re
import csv
import json
import os

def extract_pdf():
    pdf_path = "ml/data/raw/tamil_nadu_2011_results.pdf"
    
    os.makedirs("ml/data/extracted", exist_ok=True)
    os.makedirs("ml/data/cleaned", exist_ok=True)
    output_csv = "ml/data/extracted/tamil_nadu_2011_extracted.csv"
    
    constituency_re = re.compile(r'^Constituency\s+(\d+)\.\s+(.*?)\s+TOTAL ELECTORS\s*:\s*(\d+)$')
    candidate_re = re.compile(r'^(\d+)\s+(.+?)\s+([MFO])\s+(\d+)\s+(GEN|SC|ST)\s+(\S+)\s+(\d+)\s+(\d+)\s+(\d+)\s+([\d\.]+)$')
    turnout_re = re.compile(r'^TURNOUT\s+TOTAL:\s+(\d+)\s+(\d+)\s+(\d+)\s+([\d\.]+)$')
    
    data = []
    current_constituency = None
    
    ignore_starts = [
        "Election Commission",
        "DETAILED RESULTS",
        "VALID VOTES",
        "CANDIDATE NAME",
        "Page ",
        "% VOTES",
        "GENERAL",
        "POLLED"
    ]
    
    with pdfplumber.open(pdf_path) as pdf:
        name_buffer = ""
        
        for i in range(259, len(pdf.pages)):
            page = pdf.pages[i]
            text = page.extract_text()
            if not text: continue
            
            lines = text.split('\n')
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                    
                skip = False
                for ig in ignore_starts:
                    if line.startswith(ig):
                        skip = True
                        break
                if skip:
                    continue
                
                match_const = constituency_re.match(line)
                if match_const:
                    current_constituency = {
                        'number': int(match_const.group(1)),
                        'name': match_const.group(2).strip(),
                        'electors': int(match_const.group(3))
                    }
                    name_buffer = ""
                    continue
                
                match_turnout = turnout_re.match(line)
                if match_turnout:
                    continue
                
                match_cand = candidate_re.match(line)
                if match_cand:
                    full_name = (name_buffer + " " + match_cand.group(2)).strip()
                    row = {
                        'election_year': 2011,
                        'constituency_number': current_constituency['number'],
                        'constituency_name': current_constituency['name'],
                        'electors': current_constituency['electors'],
                        'position': int(match_cand.group(1)),
                        'candidate_name': full_name,
                        'sex': match_cand.group(3),
                        'age': int(match_cand.group(4)),
                        'category': match_cand.group(5),
                        'party': match_cand.group(6),
                        'general_votes': int(match_cand.group(7)),
                        'postal_votes': int(match_cand.group(8)),
                        'total_votes': int(match_cand.group(9)),
                        'vote_percentage': float(match_cand.group(10))
                    }
                    data.append(row)
                    name_buffer = "" 
                else:
                    name_buffer += " " + line

    print(f"Extracted {len(data)} rows.")
    constituencies_found = set(d['constituency_number'] for d in data)
    print(f"Constituencies found: {len(constituencies_found)}")
    missing = set(range(1, 235)) - constituencies_found
    if missing:
        print(f"Missing constituencies: {missing}")
        
    with open(output_csv, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=data[0].keys())
        writer.writeheader()
        writer.writerows(data)
        
if __name__ == '__main__':
    extract_pdf()
