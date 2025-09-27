class TicketHelper:

    def check_admin_or_user(self, user):
        if user.role == 'admin' or user.role == 'user':
            return True
        return False

    def check_admin_or_agent(self, user):
        if user.role == 'admin' or user.role == 'agent':
            return True
        return False

    def check_admin(self, user):
        if user.role == 'admin':
            return True
        return False

    def check_agent(self, user):
        if user.role == 'agent':
            return True
        return False

    def check_user(self, user):
        if user.role == 'user':
            return True
        return False

    def user_role(self, user):
        return user.role