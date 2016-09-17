Feature: Login

Background:
	Given I register the user "lucas@gmail.com" with the password "123456"

Scenario: Login successfully
	When I visit site page "/"
	Then I should see an element with id of "enter-button"
	Then I click on an element with id of "enter-button"
	And I fill in "Email" with "lucas@gmail.com"
	And I fill in "Password" with "123456"
	Then I press "Entrar"
	Then I should see "Hi, Usuário" on an element with id of "user_link"

Scenario: User does not exist
	When I visit site page "/"
	Then I should see an element with id of "enter-button"
	Then I click on an element with id of "enter-button"
	And I fill in "Email" with "leticia@hotmail.com"
	And I fill in "Password" with "lelepass"
	Then I press "Entrar"
	Then I should see "Email or Password does not match"

Scenario: Login without email
	When I visit site page "/"
	Then I should see an element with id of "enter-button"
	Then I click on an element with id of "enter-button"
	And I fill in "Email" with ""
	And I fill in "Password" with "123456"
	Then I press "Entrar"
	Then I should see an alert with text "Please fill out this field."

Scenario: Wrong password
	When I visit site page "/"
	Then I should see an element with id of "enter-button"
	Then I click on an element with id of "enter-button"
	And I fill in "Email" with "lucas@gmail.com"
	And I fill in "Password" with "password"
	Then I press "Entrar"
	Then I should see "Email or Password does not match"

	Scenario: Login without email
	When I visit site page "/"
	Then I should see an element with id of "enter-button"
	Then I click on an element with id of "enter-button"
	And I fill in "Email" with "lucas@gmail.com"
	And I fill in "Password" with ""
	Then I press "Entrar"
	Then I should see an alert with text "Please fill out this field."

Scenario: Wrong email
	When I visit site page "/"
	Then I should see an element with id of "enter-button"
	Then I click on an element with id of "enter-button"
	And I fill in "Email" with "fernando@email.com"
	And I fill in "Password" with "123456"
	Then I press "Entrar"
	Then I should see "Email or Password does not match"
