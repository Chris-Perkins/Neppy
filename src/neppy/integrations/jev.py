"""Wrapper around Jev/Laya."""

from laya import Router


class NeppyJevClient:
    def __init__(
        self,
        *,
        router_override: Router | None = None,
    ):
        self.router = router_override or Router(preload=False)

    def noul(self, state: dict, question: str) -> float:
        res = self.router.predict(
            state,
            {
                "base": {
                    "type": "noul",
                    "instructions": question,
                }
            },
        )
        return res["answers"]["base"]
