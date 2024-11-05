from odoo import _, fields
from odoo.exceptions import UserError
from odoo.http import request

from ..schemas import InspectionCreatePayload, InspectionMasterData


def get_inspection_masterdata_response_field(master_field: InspectionMasterData):
    if master_field == InspectionMasterData.project_id:
        response_field = 'address'
    elif master_field == InspectionMasterData.survey_id:
        response_field = 'title'
    else:
        response_field = 'name'
    return response_field


def validate_inspection_creation_payload(payload: InspectionCreatePayload):
    service_question_uuid = payload.service_question_uuid
    survey_uuid = payload.survey_uuid
    if survey_uuid:
        # create a new inspection from survey: not require project and task
        survey = request.env['survey.survey'].validate_by_uuid(survey_uuid)
        task = request.env['project.task'].browse_by_uuid(payload.task_uuid)
        project = request.env['project.project'].browse_by_uuid(
            payload.project_uuid)
    elif service_question_uuid:
        # create a new inspection from service_question: require project and task
        service_question = request.env['haverton.service.question'].validate_by_uuid(
            service_question_uuid)
        if not service_question.is_inspection_question:
            raise UserError(
                _('Can not create the inspection from this service question.'))
        survey = service_question.get_survey()
        task = request.env['project.task'].validate_by_uuid(payload.task_uuid)
        project = request.env['project.project'].validate_by_uuid(
            payload.project_uuid)
    else:
        raise UserError(
            _('Survey is required.'))

    if project and task.project_id != project:
        raise UserError(
            _('This activity is not in the project chosen.'))
    existed_inspection = request.env['survey.user_input'].check_inspection_existed(
        survey, task)
    if existed_inspection:
        raise UserError(
            _('An inspection has already been assigned to the user of this activity.'))

    return survey, project, task


def prepare_survey_records():
    s_ids = []
    surveys = request.env['survey.survey'].search(
        [('is_clone', '!=', True), ('active', '=', True), ('state', '=', 'published')]).sorted(key=lambda i: i.title)
    s_records = ''
    for s in surveys:
        # prepare survey record
        s_title = s.title
        dupicate_count = 0
        s_sub_id = s_title.split('.')[0].replace(' ', '_').lower(
        ) if '.' in s_title else (s_title.replace(' ', '_').lower())
        s_id = s_id_converted = 'survey_' + s_sub_id
        for s_id_info in s_ids:
            if s_id in s_id_info[0]:
                dupicate_count = s_id_info[1] + 1
                s_id_converted = s_id + '_' + str(dupicate_count)
        s_ids.append((s_id_converted, dupicate_count))
        s_record = """
        <record id="%s" model="survey.survey">
			<field name="title">%s</field>
			<field name="survey_type">%s</field>
			<field name="scoring_type">%s</field>
			<field name="questions_layout">%s</field>
			<field name="access_mode">%s</field>
			<field name="questions_selection">%s</field>
		</record>
        """ % (
            s_id_converted,
            s_title or '',
            s.survey_type or '',
            s.scoring_type or '',
            s.questions_layout or '',
            s.access_mode or '',
            s.questions_selection or '')
        s_records += s_record

        # prepare the question records
        q_records = prepare_question_records(s, s_id_converted)
        s_records += q_records

    return s_records


def prepare_question_records(survey, s_id):
    p_id = s_id
    p_count = 1
    q_count = 1
    q_records = ''
    for q in survey.question_and_page_ids.sorted(key=lambda i: i.sequence):
        if q.is_page:
            # section
            p_id = s_id + ('_quiz_p%s' % p_count)
            p_count += 1
        else:
            q_id = p_id + ('_q%s' % q_count)
            q_count += 1
        q_record = """
		<record id="%s" model="survey.question">
			<field name="title">%s</field>
			<field name="survey_id" ref="%s"/>
			<field name="sequence">%s</field>
			<field name="question_type">%s</field>
			<field name="haverton_question_type">%s</field>
			<field name="is_page" eval="%s"/>
			<field name="constr_mandatory" eval="%s"/>
			<field name="allow_no_answer" eval="%s"/>
			<field name="view_in_map" eval="%s"/>
			<field name="question_placeholder">%s</field>
			<field name="constr_error_msg">%s</field>
		</record>
        """ % (
            p_id if q.is_page else q_id,
            q.title or '',
            s_id,
            (q.sequence * 10) or 0,
            q.question_type or '',
            q.haverton_question_type or '',
            q.is_page,
            q.constr_mandatory,
            q.allow_no_answer,
            q.view_in_map,
            q.question_placeholder or '',
            q.constr_error_msg or '',
        )
        q_records += q_record

        if not q.is_page:
            # prepare the suggested_answer records
            a_records = prepare_answer_records(q, q_id)
            q_records += a_records

    return q_records


def prepare_answer_records(question, q_id):
    a_count = 1
    a_records = ''
    for a in question.suggested_answer_ids.sorted(key=lambda i: i.sequence):
        a_id = q_id + ('_a%s' % a_count)
        a_count += 1
        a_record = """
		<record id="%s" model="survey.question.answer">
			<field name="question_id" ref="%s"/>
			<field name="sequence">%s</field>
			<field name="value">%s</field>
		</record>
        """ % (
            a_id,
            q_id,
            (a.sequence * 10) or 0,
            a.value or '',
        )
        a_records += a_record

    return a_records


def get_inspections_domain(search_kwargs: dict, filter_kwargs: dict):
    """
    Returns the domain to use in the web_search_read function when gets the inspections.
    """
    domain = []
    # search
    if search_kwargs.get('q'):
        domain.append(('name', 'ilike', search_kwargs['q']))
    # filter

    overdue = filter_kwargs.get('overdue')
    status = filter_kwargs.get('status')
    uuids = filter_kwargs.get('uuids')
    if overdue:
        domain.append(('deadline', '<', fields.Date.today()))
    if status:
        domain.append(('state', '=', status.value))
    if uuids:
        domain.append(('uuid', 'in', uuids))

    return domain


def prepare_question_template_records():
    question_template = request.env['survey.question'].search([('is_page', '=', False), ('is_template', '=', True)])
    q_records = ''
    count = 1
    for q in question_template:
        q_id = f'question_template_{count}'
        count += 1
        q_record = f"""
        <record id="{q_id}" model="survey.question">
            <field name="title">{q.title or ''}</field>
            <field name="sequence">{q.sequence}</field>
            <field name="question_type">{q.question_type or ''}</field>
            <field name="haverton_question_type">{q.haverton_question_type or ''}</field>
            <field name="is_page" eval="False"/>
            <field name="is_template" eval="True"/>
            <field name="constr_mandatory" eval="{q.constr_mandatory}"/>
            <field name="allow_no_answer" eval="{q.allow_no_answer}"/>
            <field name="view_in_map" eval="{q.view_in_map}"/>
            <field name="question_placeholder">{q.question_placeholder or ''}</field>
            <field name="constr_error_msg">{q.constr_error_msg or ''}</field>
            <field name="autofill_datetime">{q.autofill_datetime}</field>
            <field name="autofill_user">{q.autofill_user}</field>
            <field name="is_required">{q.is_required}</field>
            <field name="autofill">{q.autofill}</field>   
        """
        if q.autofill_field:
            q_record += f'<field name="autofill_field">{q.autofill_field}</field>'
        else:
            q_record += '<field name="autofill_field" eval="False"/>'
        q_record += f"""
            <field name="autofill_location">{q.autofill_location}</field>
            <field name="value_static_text">{q.value_static_text or ''}</field>
            <field name="label_for_user_id">{q.label_for_user_id or ''}</field>
        </record>
        """
        
        q_records += q_record
        a_records = prepare_answer_records(q, q_id)
        q_records += a_records

    return q_records
