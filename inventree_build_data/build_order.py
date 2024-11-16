from django.urls import re_path
from django.http import HttpResponse

from build.views import BuildDetail
from plugin import InvenTreePlugin
from plugin.mixins import PanelMixin, SettingsMixin, UrlsMixin, ReportMixin
from company.models import Company, Contact
from users.models import check_user_role

import json


class BuildOrderData(PanelMixin, SettingsMixin, InvenTreePlugin, UrlsMixin, ReportMixin):

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
            'description': 'We put our own company into the database. So we can add addresses and contacts',
            'model': 'company.company',
        },
        'PARAMETER_WIDTH': {
            'name': 'Parameter for PCB width',
            'description': 'Place here the PK of the parameter used for PCB width',
            'model': 'part.partparametertemplate',
        },
        'PARAMETER_LENGTH': {
            'name': 'Parameter for PCB length',
            'description': 'Place here the PK of the parameter used for PCB length',
            'model': 'part.partparametertemplate',
        },
        'PARAMETER_LAYNO': {
            'name': 'Parameter for PCB number of layers',
            'description': 'Place here the PK of the parameter used for the number of layers in the PCB',
            'model': 'part.partparametertemplate',
        },
        'PARAMETER_DUAL': {
            'name': 'Parameter for dual side assembly',
            'description': 'Place here the PK of the parameter used for dual side assembly',
            'model': 'part.partparametertemplate',
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
        parameters = ['PARAMETER_WIDTH', 'PARAMETER_LENGTH', 'PARAMETER_LAYNO', 'PARAMETER_DUAL']
        if isinstance(view, BuildDetail):
            self.build = view.get_object()
            self.companies = Company.objects.filter(is_supplier=True)
            self.contacts = Contact.objects.filter()

            # Grab PCB data from the PCB parameters
            self.build_data = {}
            related_pcb = list(self.build.part.get_related_parts())[0]
            self.build_data['pcb_name'] = related_pcb.IPN
            for parameter in related_pcb.parameters.all():
                for par in parameters:
                    try:
                        if parameter.template.pk == int(self.get_setting(par)):
                            self.build_data[par] = parameter.data
                    except Exception:
                        self.build_data[par] = 'Parameter pk not defined'

            # Find our company and the contacts für the EMS partner
            try:
                customer_pk = int(self.get_setting('MY_PK'))
            except Exception:
                raise ValueError('MY_PK in properly set. Please check settings')
            self.customer_company = Company.objects.get(pk=customer_pk)
            self.all_customer_contacts = Contact.objects.filter(company=customer_pk)

            # Select the attachments
            for p in self.build.attachments.all():
                print('Name:', p.comment)
                print('Name:', p.attachment)

            # Calculate the total number of components on the board
            self.build_data['total_components'] = 0
            for p in self.build.part.bom_items.all():
                self.build_data['total_components'] = self.build_data['total_components'] + p.quantity

            # Grab metadata if exist and put it into the build_data dict
            try:
                self.build_data['ems_company'] = Company.objects.get(pk=self.build.metadata['ems_company_pk'])
            except Exception:
                print('error ems_company_pk')
            try:
                self.build_data['ems_contact'] = Contact.objects.get(pk=self.build.metadata['ems_contact_pk'])
            except Exception:
                print('error ems_contact_pk')
            try:
                self.build_data['customer_contact'] = Contact.objects.get(pk=self.build.metadata['customer_contact'])
            except Exception:
                print('error customer_contact')
            try:
                self.build_data['material_provisioning'] = self.build.metadata['material_provisioning']
            except Exception:
                print('error material_provisioning')
            try:
                self.build_data['sample_approval'] = self.build.metadata['sample_approval']
            except Exception:
                print('error sample_approval')

            has_permission = (check_user_role(view.request.user, 'build_order', 'change') or
                              check_user_role(view.request.user, 'build_order', 'delete') or
                              check_user_role(view.request.user, 'build_order', 'add'))
            if has_permission:
                panels.append({
                    'title': 'Manufacturig Info',
                    'icon': 'fa-industry',
                    'content_template': 'build_panel/build.html',
                })
        return panels

    def setup_urls(self):
        return [re_path(r'bocompanyselect(?:\.(?P<format>json))?$', self.process_data, name='transfer_build_data')]

# ------------------------- Helper functions ------------------------------------
    def process_data(self, request):

        data = json.loads(request.body)
        if self.build.metadata is None:
            self.build.metadata = {}
        for key in data:
            print(key, data[key])
            self.build.metadata[key] = data[key]
        self.build.save()
        self.build_data['ems_company'] = Company.objects.get(pk=self.build.metadata['ems_company_pk'])
        try:
            self.build_data['ems_contact'] = Contact.objects.get(pk=self.build.metadata['ems_contact_pk'])
        except Exception:
            pass
        self.build_data['customer_contact'] = Contact.objects.get(pk=self.build.metadata['customer_contact'])
        self.build_data['material_provisioning'] = self.build.metadata['material_provisioning']
        self.build_data['sample_approval'] = self.build.metadata['sample_approval']
        return HttpResponse('OK')

# -------------------- Add context data for report generation -------------------
    def add_report_context(self, report_instance, model_instance, request, context):

        # print('report_instance', report_instance)
        # print('request', request)
        # print('context', context)
        # print('model_instance', model_instance)

        context['build_plugin'] = self
