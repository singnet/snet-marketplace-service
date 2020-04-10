from registry.config import PUBLISHER_PORTAL_DAPP_URL, EMAIL


def get_org_member_invite_mail(org_name, invite_code):
    invite_member_template = {
        "subject": """Membership Invitation from  Organization {org_name}""",
        "body": f"""\
<html>
    <head></head>
    <body>
        <div>
            <p>Hello,</p>
            <p>Organization <em>{org_name}</em> has sent you membership invite.
                Your invite code is <strong>{invite_code}</strong>.</p><br />
            <p>Please click on the link below to
                accept the invitation.</p>
            <p>{PUBLISHER_PORTAL_DAPP_URL}</p><br /><br />
            <p>
                <em>Please do not reply to the email for any enquiries for any queries please email at
                    {EMAIL["PUBLISHER_PORTAL_SUPPORT_MAIL"]}.</em></p>
            <p>Warmest regards,<br/>SingularityNET Publisher Portal
                Team</p>
        </div>
    </body>
    
</html>\
"""
    }
    return invite_member_template


def get_service_approval_mail_template(service_id, service_name, org_id, org_name):
    service_approval_mail = {
        "subject": f"""Service Approval: service ({service_id}, {service_name}) organization ({org_id, org_name})""",
        "body": f"""\
<html>
    <head></head>
    <body>
        <div>
            <p>Hello,</p>
            <p>The following service has been submitted for approval. Please review,</p>
            <p>Service id: <strong>{service_id}</strong><br/>
            Service name: <strong>{service_name}</strong><br/>
            Organization id: <strong>{org_id}</strong><br/>
            Organization name: <strong>{org_name}</strong><br/></p>
        </div>
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

    </body>
</html>\
"""
    }
    return service_approval_mail


def get_org_approval_mail(org_id, org_name):
    org_approval_mail = {
        "subject": f"""Organization Approval: organization ({org_id, org_name})""",
        "body": f"""\
<html>
    <head></head>
    <body>
        <div>
            <p>Hello,</p>
            <p>The following organization has been submitted for approval. Please review,</p>
            <p>Organization id: <strong>{org_id}</strong><br/>
            Organization name: <strong>{org_name}</strong><br/></p>
        </div>
        <br/>

        <i><p>Steps for approval:</p>
        <ul>
            <li>Go to approval channel</li>
            <li><strong>/list-orgs-for-approval</strong> command to get list of services</li>
            <li>To review the particular service click on <strong>review</strong>, it will open pop up window</li>
            <li>Select appropriate options (Approved, Rejected, Change requested) and give comment.</li>
            <li>Click on <strong>submit</strong> to review the service.</li>
        </ul></i>
        
        <br/>
        <p>Regards,<br/>SingularityNET Publisher Portal Team</p>

    </body>
</html> \
"""
    }
    return org_approval_mail
