from django.contrib.auth.models import User
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.webdriver import WebDriver
from selenium.common.exceptions import NoSuchElementException


class MySeleniumTests(StaticLiveServerTestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        opts = Options()
        cls.selenium = WebDriver(options=opts)
        cls.selenium.implicitly_wait(5)
        # creem superusuari
        user = User.objects.create_user("isard", "isard@isardvdi.com", "pirineus")
        user.is_superuser = True
        user.is_staff = True
        user.save()

    @classmethod
    def tearDownClass(cls):
        cls.selenium.quit()
        super().tearDownClass()

    def test_login(self):
        self.selenium.get(f"{self.live_server_url}/admin/login/")
        self.assertEqual(self.selenium.title, "Log in | Django site admin")

        self.selenium.find_element(By.NAME, "username").send_keys("isard")
        self.selenium.find_element(By.NAME, "password").send_keys("pirineus")
        self.selenium.find_element(By.XPATH, '//input[@value="Log in"]').click()

        self.assertEqual(self.selenium.title, "Site administration | Django site admin")

        self.assertEqual(self.selenium.title, "Site administration | Django site admin")

        # 2. anem a la llista d'usuaris i a "Add user"
        self.selenium.find_element(By.LINK_TEXT, "Users").click()
        self.selenium.find_element(By.XPATH, "//a[@href='/admin/auth/user/add/']").click()

        # 3. omplim el formulari del nou usuari i desem
        self.selenium.find_element(By.NAME, "username").send_keys("becari")
        self.selenium.find_element(By.NAME, "password1").send_keys("Tarragona2026!")
        self.selenium.find_element(By.NAME, "password2").send_keys("Tarragona2026!")
        self.selenium.find_element(By.NAME, "_save").click()

        # comprovem que som a la pàgina d'edició de l'usuari nou
        self.assertIn("Change user", self.selenium.title)

        # 4. marquem "Staff status" i donem el permís "Can view user"
        self.selenium.find_element(By.NAME, "is_staff").click()
        self.selenium.find_element(By.XPATH, "//select[@id='id_user_permissions_from']/option[text()='Authentication and Authorization | user | Can view user']").click()
        self.selenium.find_element(By.ID, "id_user_permissions_add").click()
        self.selenium.find_element(By.NAME, "_save").click()

        # comprovem que hem tornat a la llista d'usuaris
        self.assertEqual(self.selenium.title, "Select user to change | Django site admin")

        # 5. tanquem la sessió d'isard
        self.selenium.find_element(By.XPATH, "//button[text()='Log out']").click()
        self.assertEqual(self.selenium.title, "Logged out | Django site admin")

        # 6. entrem amb l'usuari nou
        self.selenium.get(f"{self.live_server_url}/admin/login/")
        self.selenium.find_element(By.NAME, "username").send_keys("becari")
        self.selenium.find_element(By.NAME, "password").send_keys("Tarragona2026!")
        self.selenium.find_element(By.XPATH, '//input[@value="Log in"]').click()
        self.assertEqual(self.selenium.title, "Site administration | Django site admin")

        # 7. comprovem que SÍ pot veure la llista d'usuaris
        self.selenium.find_element(By.LINK_TEXT, "Users").click()
        self.assertEqual(self.selenium.title, "Select user to view | Django site admin")

        # 8. comprovem que NO pot crear usuaris: no hi ha el botó "Add user"
        try:
            self.selenium.find_element(By.XPATH, "//a[@href='/admin/auth/user/add/']")
            assert False, "Trobat el botó 'Add user' i no hi hauria de ser"
        except NoSuchElementException:
            pass

        # 9. comprovem que NO pot esborrar usuaris: no hi ha el botó "Delete"
        self.selenium.find_element(By.LINK_TEXT, "isard").click()
        self.assertIn("View user", self.selenium.title)
        try:
            self.selenium.find_element(By.XPATH, "//a[contains(@class, 'deletelink')]")
            assert False, "Trobat el botó 'Delete' i no hi hauria de ser"
        except NoSuchElementException:
            pass
