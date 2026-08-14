import unittest

from logosweaver import ResponseMode, ResponseOutputBoundary, ResponsePermission


class ResponseOutputBoundaryV05Tests(unittest.TestCase):
    def setUp(self):
        self.boundary = ResponseOutputBoundary()
        self.permission = ResponsePermission(
            ResponseMode.CLARIFY,
            "NEED_INTEGRITY_UNRESOLVED",
            "f-1",
        )

    def test_permitted_mode_is_admitted(self):
        admission = self.boundary.admit(self.permission, ResponseMode.CLARIFY)
        self.assertTrue(admission.admitted)
        self.assertEqual(admission.permitted_mode, ResponseMode.CLARIFY)

    def test_unpermitted_allow_is_rejected(self):
        admission = self.boundary.admit(self.permission, ResponseMode.ALLOW)
        self.assertFalse(admission.admitted)
        self.assertEqual(admission.reason, "RESPONSE_MODE_NOT_PERMITTED")

    def test_stop_rejects_every_requested_mode(self):
        permission = ResponsePermission(ResponseMode.STOP, "EXPLICIT_RUNTIME_STOP", "f-1")
        for mode in ResponseMode:
            admission = self.boundary.admit(permission, mode)
            self.assertFalse(admission.admitted)
            self.assertEqual(admission.reason, "RESPONSE_STOPPED")

    def test_identity_reflection_permission_does_not_admit_allow(self):
        permission = ResponsePermission(
            ResponseMode.REFLECT,
            "IDENTITY_UNRESOLVED",
            "f-1",
        )
        admission = self.boundary.admit(permission, ResponseMode.ALLOW)
        self.assertFalse(admission.admitted)
        self.assertEqual(admission.permitted_mode, ResponseMode.REFLECT)


if __name__ == "__main__":
    unittest.main()
