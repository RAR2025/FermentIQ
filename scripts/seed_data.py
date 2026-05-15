#!/usr/bin/env python
import requests
import os

BACKEND = os.getenv('BACKEND_URL', 'http://localhost:8000')

def main():
    try:
        r = requests.get(BACKEND.rstrip('/') + '/api/simulate/')
        print('simulate:', r.status_code)
        r2 = requests.get(BACKEND.rstrip('/') + '/api/analyze/')
        print('analyze:', r2.status_code)
        print(r2.text)
    except Exception as e:
        print('Error contacting backend:', e)

if __name__ == '__main__':
    main()
