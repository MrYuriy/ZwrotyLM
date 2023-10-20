from django.core.management.base import BaseCommand
from django.conf import settings
from oauth2client.service_account import ServiceAccountCredentials
import httplib2
import apiclient.discovery


class Command(BaseCommand):
    def handle(self, *args, **options):
        body = {
            "values": [
                ["test", "test", "test", "test", "test"],


            ]
        }
        sheet_name = "Zwroty_LM"
        creds_file = settings.CREDENTIALS_FILE_PATH
        spreadsheet_id = settings.SPREADSHEET_ID

        credentials = ServiceAccountCredentials.from_json_keyfile_name(
            creds_file,
            ['https://www.googleapis.com/auth/spreadsheets',
             'https://www.googleapis.com/auth/drive'])

        httpAuth = credentials.authorize(httplib2.Http())
        service = apiclient.discovery.build('sheets', 'v4', http=httpAuth)

        response = (
            service.spreadsheets()
            .values()
            .get(
                spreadsheetId=spreadsheet_id, range=sheet_name
            )
            .execute()
        )

        values = response.get("values", [])

        start_row = len(values) + 1
        finish_row = start_row + len(body['values'][0])
        range_to_write = f"{sheet_name}!A{start_row}:G{finish_row}"
        response = service.spreadsheets().values().update(
            spreadsheetId=spreadsheet_id,
            range=range_to_write,
            valueInputOption="RAW",
            body=body,
        ).execute()
