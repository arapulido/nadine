import traceback
from datetime import datetime, timedelta, date

from django.conf import settings
from django.test import TestCase
from django.core import management
from django.contrib.auth.models import User

from interlink.tests.test_utils import create_user

from interlink.models import MailingList, IncomingMail, OutgoingMail
from interlink import DEFAULT_MAIL_CHECKER, TestMailChecker, TEST_INCOMING_MAIL, add_test_incoming

class ListTest(TestCase):

   def setUp(self):
      self.user1, self.client1 = create_user('alice', 'Alice', 'Dodgson', is_staff=True)
      self.user2, self.client2 = create_user('bob', 'Bob', 'Albert')
      self.mlist1 = MailingList.objects.create(
         name='Hat Styles', description='All about les chapeau', subject_prefix='hat',
         email_address='hats@example.com', username='hat', password='1234',
         pop_host='localhost', smtp_host='localhost'
      )
      
   def test_recipients(self):
      self.assertEqual(len(self.mlist1.subscriber_addresses), 0)
      self.assertEqual(len(self.mlist1.moderator_addresses), 0)
      self.mlist1.subscribers.add(self.user2)
      self.assertEqual(len(self.mlist1.subscriber_addresses), 1)
      self.assertEqual(len(self.mlist1.moderator_addresses), 0)
      self.mlist1.moderators.add(self.user1)
      self.assertEqual(len(self.mlist1.subscriber_addresses), 1)
      self.assertEqual(len(self.mlist1.moderator_addresses), 1)
   
   def test_mail_checking(self):
      self.assertEqual(DEFAULT_MAIL_CHECKER, TestMailChecker)
      checker = DEFAULT_MAIL_CHECKER(self.mlist1)
      add_test_incoming(self.mlist1, 'alice@example.com', 'ahoi', 'I like traffic lights.', sent_time=datetime.now() - timedelta(minutes=15))
      self.assertEqual(IncomingMail.objects.all().count(), 0)
      in_mail = checker.fetch_mail()
      self.assertEqual(len(in_mail), 1)
      self.assertEqual(in_mail[0].origin_address, 'alice@example.com')
      self.assertEqual(IncomingMail.objects.all().count(), 1)

      add_test_incoming(self.mlist1, 'alice@example.com', 'ahoi 2', 'I like traffic lights A LOT.', sent_time=datetime.now() - timedelta(minutes=15))
      self.assertEqual(MailingList.objects.fetch_all_mail(), [])
      self.assertEqual(IncomingMail.objects.all().count(), 2)
      
# Copyright 2011 Office Nomads LLC (http://www.officenomads.com/) Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except in compliance with the License. You may obtain a copy of the License at http://www.apache.org/licenses/LICENSE-2.0 Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.
