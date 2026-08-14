import unittest

from logosweaver import (
    DialogueResponse,
    ResponseEmitter,
    ResponseMode,
    ResponsePermission,
)


class ResponseEmitterV05Tests(unittest.TestCase):
    def setUp(self):
        self.emitter = ResponseEmitter()
        self.permission = ResponsePermission(
            ResponseMode.CLARIFY,
            "NEED_INTEGRITY_UNRESOLVED",
            "f-1",
        )

    def test_permitted_response_is_emitted(self):
        response = DialogueResponse(ResponseMode.CLARIFY, "Please clarify the intended scope.", "f-1")
        result = self.emitter.emit(self.permission, response)
        self.assertTrue(result.emitted)
        self.assertEqual(result.reason, "RESPONSE_EMITTED")
        self.assertEqual(result.response.content, response.content)

    def test_unpermitted_allow_response_is_not_emitted(self):
        response = DialogueResponse(ResponseMode.ALLOW, "The user's true need is X.", "f-1")
        result = self.emitter.emit(self.permission, response)
        self.assertFalse(result.emitted)
        self.assertEqual(result.reason, "RESPONSE_MODE_NOT_PERMITTED")

    def test_stop_permission_blocks_output(self):
        permission = ResponsePermission(ResponseMode.STOP, "EXPLICIT_RUNTIME_STOP", "f-1")
        response = DialogueResponse(ResponseMode.CLARIFY, "We should pause here.", "f-1")
        result = self.emitter.emit(permission, response)
        self.assertFalse(result.emitted)
        self.assertEqual(result.reason, "RESPONSE_STOPPED")

    def test_figure_identity_is_not_crossed_at_output_boundary(self):
        response = DialogueResponse(ResponseMode.CLARIFY, "Clarify this.", "f-2")
        result = self.emitter.emit(self.permission, response)
        self.assertFalse(result.emitted)
        self.assertEqual(result.reason, "FIGURE_ID_MISMATCH")


if __name__ == "__main__":
    unittest.main()
