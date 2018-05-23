import unittest2 as unittest
from plone import api


class organsTestBase(unittest.TestCase):

    def create_organ(self, id='organ-govern', name=u'organ-govern', organ_type='Closed'):
        """ Creates an organ folder, and the custom organ_type. Only Manager can create Organs  """

        if api.user.is_anonymous():
            self.assertTrue(False, msg='Tried to create an Organ without permissions.')

        if 'Manager' not in api.user.get_roles():
            self.assertTrue(False, msg='Tried to create an Organ but the user has not enough permissions to do so.')

        organ_folder = api.content.create(
            type='genweb.organs.organgovern',
            title='Consell de Govern',
            id='consell-de-govern',
            container=self.portal['ca']['folder-organs'])

        return organ_folder.id
