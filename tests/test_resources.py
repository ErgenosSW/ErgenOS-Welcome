from unittest import TestCase

from ergenos_welcome.resources import (
    ERGENOS_BUG_REPORT,
    online_resources,
    preferred_language,
)


class ResourcesTests(TestCase):
    def test_language_names_are_normalized(self) -> None:
        self.assertEqual(preferred_language(("pl_PL.UTF-8", "pl", "C")), "pl")
        self.assertEqual(preferred_language(("pl-PL", "pl", "C")), "pl")
        self.assertEqual(preferred_language(("en_US.UTF-8", "en", "C")), "en")
        self.assertEqual(preferred_language(()), "en")

    def test_polish_resources_use_polish_pages(self) -> None:
        resources = online_resources(("pl_PL.UTF-8", "pl", "C"))
        self.assertEqual(resources[0].title, "Oficjalna strona")
        self.assertEqual(resources[0].uri, "https://ergenossw.github.io/ErgenOS-Website/pl/")
        self.assertEqual(resources[1].uri, "https://ergenossw.github.io/ErgenOS-Wiki/pl/")

    def test_english_resources_use_default_pages(self) -> None:
        resources = online_resources(("en_US.UTF-8", "en", "C"))
        self.assertEqual(resources[0].title, "Official website")
        self.assertEqual(resources[0].uri, "https://ergenossw.github.io/ErgenOS-Website/")
        self.assertEqual(resources[1].uri, "https://ergenossw.github.io/ErgenOS-Wiki/")
        self.assertEqual(resources[3].uri, ERGENOS_BUG_REPORT)
