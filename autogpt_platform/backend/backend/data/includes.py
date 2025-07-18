from typing import Sequence, cast

import prisma.enums
import prisma.types

AGENT_NODE_INCLUDE: prisma.types.AgentNodeInclude = {
    "Input": True,
    "Output": True,
    "Webhook": True,
    "AgentBlock": True,
}

AGENT_GRAPH_INCLUDE: prisma.types.AgentGraphInclude = {
    "Nodes": {"include": AGENT_NODE_INCLUDE}
}

EXECUTION_RESULT_ORDER: list[prisma.types.AgentNodeExecutionOrderByInput] = [
    {"queuedTime": "desc"},
    # Fallback: Incomplete execs has no queuedTime.
    {"addedTime": "desc"},
]

EXECUTION_RESULT_INCLUDE: prisma.types.AgentNodeExecutionInclude = {
    "Input": {"order_by": {"time": "asc"}},
    "Output": {"order_by": {"time": "asc"}},
    "Node": True,
    "GraphExecution": True,
}

MAX_NODE_EXECUTIONS_FETCH = 1000

GRAPH_EXECUTION_INCLUDE_WITH_NODES: prisma.types.AgentGraphExecutionInclude = {
    "NodeExecutions": {
        "include": EXECUTION_RESULT_INCLUDE,
        "order_by": EXECUTION_RESULT_ORDER,
        "take": MAX_NODE_EXECUTIONS_FETCH,  # Avoid loading excessive node executions.
    }
}


def graph_execution_include(
    include_block_ids: Sequence[str],
) -> prisma.types.AgentGraphExecutionInclude:
    return {
        "NodeExecutions": {
            **cast(
                prisma.types.FindManyAgentNodeExecutionArgsFromAgentGraphExecution,
                GRAPH_EXECUTION_INCLUDE_WITH_NODES["NodeExecutions"],  # type: ignore
            ),
            "where": {
                "Node": {
                    "is": {"AgentBlock": {"is": {"id": {"in": include_block_ids}}}}
                },
                "NOT": [
                    {"executionStatus": prisma.enums.AgentExecutionStatus.INCOMPLETE}
                ],
            },
        }
    }


INTEGRATION_WEBHOOK_INCLUDE: prisma.types.IntegrationWebhookInclude = {
    "AgentNodes": {"include": AGENT_NODE_INCLUDE},
    "AgentPresets": {"include": {"InputPresets": True}},
}


def library_agent_include(user_id: str) -> prisma.types.LibraryAgentInclude:
    return {
        "AgentGraph": {
            "include": {
                **AGENT_GRAPH_INCLUDE,
                "Executions": {"where": {"userId": user_id}},
            }
        },
        "Creator": True,
    }
