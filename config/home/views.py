from django.shortcuts import render
from typing import Any
from django.shortcuts import render, redirect
from django.views import View
import paramiko
from django.contrib.auth import logout
from django.contrib import messages


class HomeView(View):
    def get(self, request):
        return render(request, 'home.html')


# login page
class LoginView(View):
    def get(self, request):
        if request.session.get('is_logged_in'):
            return redirect('home')

        return render(request, 'login.html')

    def post(self, request):
        if request.method == 'POST':
            username = request.POST.get('username')
            password = request.POST.get('password')
            ip = request.POST.get('ip')
            port = int(request.POST.get('port', 22))

            try:
                client = paramiko.SSHClient()
                client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                client.connect(ip, port=port, username=username, password=password)

                request.session['is_logged_in'] = True
                request.session['ip'] = ip
                request.session['port'] = port
                request.session['username'] = username
                request.session['password'] = password

                return render(request, 'home.html', {'ip': ip})
            except paramiko.AuthenticationException:
                messages.error(request, 'ورود ناموفق بود', 'danger')

            except paramiko.SSHException as e:
                messages.error(request, f'error message:{str(e)}', 'danger')

        return render(request, 'login.html')


def my_view(request):
    is_logged_in = request.session.get('is_logged_in')
    return render(request, 'inc/navbar.html', {'is_logged_in': is_logged_in})


# create user
class CreateUserView(View):
    def get(self, request):
        if not request.session.get('is_logged_in'):
            return redirect('login')
        return render(request, 'create_user.html')

    def post(self, request):
        if not request.session.get('is_logged_in'):
            return redirect('login')

        if request.method == 'POST':
            new_username = request.POST.get('new_username')
            new_password = request.POST.get('new_password')

            try:
                adduser_cmd = f'sudo adduser {new_username}'
                client = paramiko.SSHClient()
                client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                client.connect(request.session['ip'], port=request.session['port'],
                               username=request.session['username'], password=request.session['password'])

                stdin, stdout, stderr = client.exec_command(adduser_cmd, get_pty=True)
                stdin.write(f"{new_password}\n{new_password}\n")
                stdin.flush()

                messages.success(request, f'created new user with username: {new_username}', 'success')
            except paramiko.SSHException as e:
                messages.error(request, f'error message: {str(e)}', 'danger')

        return render(request, 'create_user.html')


# delete user

class DeleteUserView(View):
    def get(self, request):

        if not request.session.get('is_logged_in'):
            return redirect('login')
        return render(request, 'delete_user.html')

    def post(self, request):
        if request.method == 'POST':
            username = request.POST.get('username')

            try:

                client = paramiko.SSHClient()
                client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                client.connect(request.session['ip'], port=request.session['port'],
                               username=request.session['username'], password=request.session['password'])

                killall_cmd = f'sudo killall -u {username}'
                deluser_cmd = f'sudo deluser {username}'
                remove_home_dir_cmd = f'sudo rm -rf /home/{username}'

                stdin, stdout, stderr = client.exec_command(killall_cmd)
                stdin.write('Y\n')
                stdin.flush()

                stdin, stdout, stderr = client.exec_command(deluser_cmd)
                stdin.write('Y\n')
                stdin.flush()

                stdin, stdout, stderr = client.exec_command(remove_home_dir_cmd)

                messages.success(request, f'deleted user {username}', 'danger')
            except paramiko.SSHException as e:
                messages.error(request, request, str(e), 'danger')

        return render(request, 'delete_user.html')


class LogoutView(View):
    def get(self, request):
        if not request.session.get('is_logged_in'):
            return redirect('login')

        logout(request)
        return redirect('login')
