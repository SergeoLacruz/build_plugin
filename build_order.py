from django.urls import re_path
from django.http import HttpResponse

from build.views import BuildDetail
from build.models import Build
from plugin import InvenTreePlugin
from plugin.mixins import PanelMixin, SettingsMixin, UrlsMixin, ReportMixin
from company.models import Company, Contact
from users.models import check_user_role

import json

class BuildOrderPanel(PanelMixin, SettingsMixin, InvenTreePlugin, UrlsMixin, ReportMixin):

    # Define data that is displayed on the panel

    NAME = "BuildOrderData"
    SLUG = "buildorderdata"
    TITLE = "Additional data for build orders"
    AUTHOR = "Michael"
    PUBLISH_DATE = "2023-11-11:00:00"
    DESCRIPTION = "This plugin adds data for external manufacturing to a build order"
    VERSION = '0.0.1'

    SETTINGS = {
        'MY_PK': {
            'name': 'PK of our company',
            'description': 'We put our own company int othe database. So we can add addresses and contacts',
            'model': 'company.company',
        },
    }

# Create some help  
    def get_settings_content(self, request):
        return """
        <p>Setup:</p>
        <ol>
        <li>Enable the plugin</li>
        <li>RTFM</li>
        <li>Enter additional data to the Manufacturing Info panel</li>
        <li>Create reports with additiona context variables</li>
        <li>Enjoy</li>
        """

# Create the panel that will display on the BuildOrder view,
    def get_custom_panels(self, view, request):
        panels = []
        if isinstance(view, BuildDetail):
            self.build=view.get_object()
            self.companies=Company.objects.filter(is_supplier=True)
            self.contacts=Contact.objects.filter()
            self.RelatedPCB=list(self.build.part.get_related_parts())[0]

            try:
                customer_pk=int(self.get_setting('MY_PK'))
            except:
                raise ValueError('MY_PK in properly set. Please check settings')       
            self.customer_company=Company.objects.get(pk=customer_pk)
            self.all_customer_contacts=Contact.objects.filter(company=customer_pk)

            # Select the attachments
            for p in self.build.attachments.all():
                print('Name:',p.comment)
                print('Name:',p.attachment)

            # Calculate the total number of components on the board
            self.total_components=0
            for p in self.build.part.bom_items.all():
                self.total_components = self.total_components + p.quantity

            # Grab metadata if exist and create the context variables for the report
            try:
                self.ems=Company.objects.get(pk=self.build.metadata['ems_company_pk'])
            except:
                print('error ems_company_pk')
            try:
                self.ems_contact=Contact.objects.get(pk=self.build.metadata['ems_contact_pk'])
            except:
                print('error ems_contact_pk')
            try:
                self.customer_contact=Contact.objects.get(pk=self.build.metadata['customer_contact'])
            except:
                print('error customer_contact')

            has_permission=(check_user_role(view.request.user, 'build_order','change') or 
                           check_user_role(view.request.user, 'build_order','delete') or
                           check_user_role(view.request.user, 'build_order','add'))
            if has_permission:
                panels.append({
                    'title': 'Manufacturig Info',
                    'icon': 'fa-industry',
                    'content_template': 'build_panel/build.html', 
                })
        return panels

    def setup_urls(self):
        return [
                re_path(r'bocompanyselect(?:\.(?P<format>json))?$', self.process_data, name='transfer_build_data'),
               ]

#------------------------- Helper functions ------------------------------------
    def process_data(self,request):

        data=json.loads(request.body)
        if self.build.metadata is None:
            self.build.metadata={}
        for key in data:
            print(key, data[key])
            self.build.metadata[key]=data[key]
        self.build.save()
        return HttpResponse(f'OK')

#-------------------- Add context data for report generation -------------------
    def add_report_context(self, report_instance, model_instance, request, context):

#        print('report_instance', report_instance)
#        print('request', request)
#        print('context', context)
#        print('model_instance', model_instance)

        context['build_plugin'] = self




