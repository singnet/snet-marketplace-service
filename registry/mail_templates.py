from registry.settings import settings


def get_org_member_invite_mail(org_name, invite_code):
    invite_member_template = {
        "subject": f"""Membership Invitation from  Organization {org_name}""",
        "body": f"""<div>
                <p>Hello,</p>
                <p>Organization <em>{org_name}</em> has sent you membership invite.
                    Your invite code is <strong>{invite_code}</strong></p><br />
                <p>Please click on the link below to
                    accept the invitation.</p>
                <p>{settings.emails.PUBLISHER_PORTAl_DAPP_URL}?invite_code={invite_code}</p><br /><br />
                <p>
                    <em>Please do not reply to the email for any enquiries for any queries please email at
                        {settings.emails.PUBLISHER_PORTAL_SUPPORT_MAIL}.</em></p>
                <p>Warmest regards,<br/>SingularityNET Publisher Portal
                    Team</p>
            </div>"""
    }
    return invite_member_template


def get_service_approval_mail_template(service_id, service_name, org_id, org_name):
    service_approval_mail = {
        "subject": f"""Service Approval: service ({service_id}, {service_name}) organization ({org_id}, {org_name})""",
        "body": f"""\
<div>
    <p>Hello,</p>
    <p>The following service has been submitted for approval. Please review,</p>
    <p>Service id: <strong>{service_id}</strong><br/>
    Service name: <strong>{service_name}</strong><br/>
    Organization id: <strong>{org_id}</strong><br/>
    Organization name: <strong>{org_name}</strong><br/></p>
    <br/>
    <i><p>Steps for approval:</p>
        <ul>
            <li>Go to approval channel</li>
            <li><strong>/list-services-for-approval 5</strong> command to get list of services</li>
            <li>To review the particular service click on <strong>review</strong>, it will open pop up window</li>
            <li>Which will contain a link to test the service.</li>
            <li>Select appropriate options (Approved, Rejected, Change requested) and give comment.</li>
            <li>Click on <strong>submit</strong> to review the service.</li>
        </ul></i>
            
    <br/>
    <p>Regards,<br/>SingularityNET Publisher Portal Team</p>
</div> \
"""
    }
    return service_approval_mail


def get_org_approval_mail(org_id, org_name):
    org_approval_mail = {
        "subject": f"""Organization Approval: organization ({org_id}, {org_name})""",
        "body": f"""\
<div>
    <p>Hello,</p>
    <p>The following organization has been submitted for approval. Please review,</p>
    <p>Organization id: <strong>{org_id}</strong><br/>
    Organization name: <strong>{org_name}</strong><br/></p>
    <br/>
    
    <i><p>Steps for approval:</p>
        <ul>
            <li>Go to approval channel</li>
            <li><strong>/list-orgs-for-approval</strong> command to get list of services</li>
            <li>To review the particular service click on <strong>review</strong>, it will open pop up window</li>
            <li>Select appropriate options (Approved, Rejected, Change requested) and give comment.</li>
            <li>Click on <strong>submit</strong> to review the service.</li>
        </ul>
    </i>
    <br/>
    <p>Regards,<br/>SingularityNET Publisher Portal Team</p>
</div> \
"""
    }
    return org_approval_mail


def get_notification_mail_template_for_service_provider_when_org_is_submitted_for_onboarding(org_id):
    mail_template = {
        "subject": f"Your organization {org_id} has successfully submitted for approval",
        "body": f"""<div>Your organization {org_id} has successfully been submitted for approval. We will notify you once it 
        is reviewed by our approval team. It usually takes around five to ten business days for approval.
        <br/>
        <p>Regards,<br/>SingularityNET Publisher Portal Team</p>
        </div>
        """
    }
    return mail_template


def get_owner_mail_for_org_rejected(org_id, comment):
    mail_template = {
        "subject": f"Your organization {org_id} has been reviewed",
        "body": f"""
<div>
    <p>Hello!</p>
    Your organization {org_id} has been reviewed and does not pass our acceptance criteria due to the 
following reasons,<br/>
    {comment}
    
    <p>Regards,<br/>SingularityNET Publisher Portal Team</p>
</div>"""
    }
    return mail_template


def get_owner_mail_for_org_approved(org_id):
    mail_template = {
        "subject": f"Your organization {org_id} has been reviewed",
        "body": f"""
<div>
    <p>Hello!</p>
    Your organization {org_id} has been reviewed, and it is approved by our approval team.<br/>
    
    <p>Regards,<br/>SingularityNET Publisher Portal Team</p>
</div>"""
    }
    return mail_template


def get_owner_mail_for_org_changes_requested(org_id, comment):
    mail_template = {
        "subject": f"Your organization {org_id} has been reviewed",
        "body": f"""
<div>
    <p>Hello!</p>
    Your organization {org_id} has been reviewed, and changes are requested by our approval 
team with following comment in review,<br/>
    <strong>Comment:</strong> {comment}
    
    <p>Regards,<br/>SingularityNET Publisher Portal Team</p>
</div>"""
    }
    return mail_template
