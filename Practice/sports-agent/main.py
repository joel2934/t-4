from langchain_core.messages import HumanMessage

from agent import sports_app


def main():

    print(
        "=========================================="
    )

    print(
        "       🏏 CRICKET SPORTS AGENT"
    )

    print(
        "=========================================="
    )


    user_question = input(
        "\nAsk me something about cricket: "
    )


    result = sports_app.invoke(

        {
            "messages": [
                HumanMessage(
                    content=user_question
                )
            ]
        }

    )


    print(
        "\n=========================================="
    )

    print(
        "FINAL ANSWER"
    )

    print(
        "=========================================="
    )


    final_message = (
        result["messages"][-1]
    )


    print(
        final_message.content
    )


if __name__ == "__main__":

    main()