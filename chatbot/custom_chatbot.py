import os
from typing import Optional, TypedDict

from dotenv import load_dotenv
from langchain.chat_models import ChatOpenAI
from langchain.embeddings import OpenAIEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_core.output_parsers import JsonOutputParser, StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langgraph.graph import END, StateGraph
import nltk

from chatbot.testcode.testcode_generator import generate_unit_test, save_test

nltk.download('punkt_tab')
nltk.download('averaged_perceptron_tagger_eng')

load_dotenv()
api_key = os.environ.get("OPENAI_API_KEY")


class State(TypedDict):
    question: str
    generation: str
    data: str
    category: Optional[str]
    code_uploaded: bool  # code 파일 업로드 여부


class CodeChatbot:
    def __init__(
        self,
        code : Optional[str] = None,
        code_path: Optional[str] = None,
        code_uploaded: bool = False,  # code 파일 업로드 여부
    ) -> None:
        """
        Chatbot을 초기화합니다.

        Args:
            code : Optional[str]: 코드
            code_path (Optional[str], optional): Code 경로
            code_uploaded (bool, optional): Code 업로드 상태
        """
        self.code_uploaded = code_uploaded  # code_uploaded 상태 저장
        self.code = code

        # RAG에 활용할 LLM
        if "OPENAI_API_KEY" not in os.environ:
            os.environ["OPENAI_API_KEY"] = os.getenv('OPENAI_API_KEY')
        self.llm = ChatOpenAI(temperature=0, model="gpt-4o-mini")

        # 질문 프롬프트 라우팅에 활용할 LLM
        self.route_llm =  ChatOpenAI(temperature=0, model="gpt-4o-mini")

        # 그래프 초기화
        self.graph = StateGraph(State)

        # 노드 추가
        # "init_answer" 노드는 self.route_question을 호출
        # "code_review" 노드는 self.review을 호출
        # "code_refactor" 노드는 self.refactor을 호출
        # "plain_answer" 노드는 self.answer를 호출
        # "answer_with_retrieval" 노드는 self.answer_with_retrieved_data를 호출
        self.graph.add_node('init_answer',self.route_question)
        self.graph.add_node('code_review', self.code_review)
        self.graph.add_node('code_refactor',self.code_refactor)
        self.graph.add_node('check_convention',self.check_convention)
        self.graph.add_node('generate_test_code',self.generate_test_code)
        self.graph.add_node('plain_answer', self.answer)
        self.graph.add_node('answer_with_retrieval', self.answer_with_retrieved_data)

        # 시작점 설정
        self.graph.set_entry_point("init_answer")

        # 간선 추가
        # "plain_answer"에서 END로 연결
        # "answer_with_retrieval"에서 END로 연결
        self.graph.add_edge('plain_answer',END)
        self.graph.add_edge('answer_with_retrieval',END)
        self.graph.add_edge('code_review','answer_with_retrieval')
        self.graph.add_edge('code_refactor','answer_with_retrieval')
        self.graph.add_edge('check_convention','answer_with_retrieval')
        self.graph.add_edge('generate_test_code',END)

        # 조건부 간선 추가
        # "plain_answer" 조건은 "plain_answer" 노드로 연결
        self.graph.add_conditional_edges(
            "init_answer",
            self._extract_route,
            {
                "code_review": "code_review",
                "code_refactor": "code_refactor",
                "check_convention": "check_convention",
                "generate_test_code": "generate_test_code",
                "plain_answer": "plain_answer",
            },
        )

        self.graph = self.graph.compile()

    def invoke(self, question) -> str:
        # TODO: self.graph의 invoke 메서드를 사용하여 {"question": question}을 입력으로 전달하고, 결과를 answer 변수에 저장하는 코드를 작성하세요.
        answer = self.graph.invoke({"question": question})
        return answer

    def code_review(self, state: State):
        """
        code review 
        """
        question = state["question"]
        data = self.code

        return {"question": question, "data": data, "category": "code_review"}

    def code_refactor(self, state: State):
        """
        code review 
        """
        question = state["question"]
        data = self.code

        return {"question": question, "data": data, "category": "code_refactor"}

    def check_convention(self, state: State):
        """
        code review 
        """
        question = state["question"]
        data = self.code

        return {"question": question, "data": data, "category": "check_convention"}

    def generate_test_code(self, state: State):
        """
        code review 
        """
        question = state["question"]
        data = self.code

        test_code = generate_unit_test(data)
        save_test('Test.java',test_code)

        return {
            "question": question,
            "generation": '```java'+test_code+'\n```' + '\n(generate_test_code)',
            "category": 'generate_test_code',
        }

    def answer(self, state: State):
        """
        일반 답변 생성
        """
        question = state["question"]

        return {
            "question": question,
            "generation": self.llm.invoke(question).content,
            "category": None,
        }

### TODO : 챗봇의 응답 후 가공
    def answer_with_retrieved_data(self, state: State):
        """
        검색 데이터 기반 답변 생성
        """
        question = state["question"]
        data = state["data"]
        category = state.get("category", None)  # 출처 정보 가져오기

        # 데이터 출처별 시스템 프롬프트 설정
        base_prompt = """
            당신은 사용자의 질문에 자세하게 답변하는 QA 챗봇입니다. 
            사용자가 입력하는 정보를 바탕으로 질문에 답하세요.
        """

        # if category == "재무제표":
        #     system_prompt = (
        #         base_prompt
        #         + """
        #         재무제표의 모든 숫자는 백만원 단위입니다. 답변할 때 숫자의 단위를 명확히 표시해주세요.
        #         예를 들어, 재무제표에서 "1,000"이라는 숫자가 나오면 이는 "10억원"을 의미합니다. 
        #     """
        #     )
        # else:
        system_prompt = base_prompt

        messages = [
            ("system", system_prompt),
            ("human", "\n질문: {question}.\n문서: {context}.\n"),
        ]

        # messages를 사용해 ChatPromptTemplate을 생성하고 이를 prompt에 저장하세요.
        # prompt를 self.llm 및 StrOutputParser()와 연결하여 체인을 구성하세요.
        # {"context": data, "question": question}을 입력으로 전달하여 generation 변수에 저장하는 코드를 작성하세요.
        prompt = ChatPromptTemplate(messages)
        chain = prompt | self.llm | StrOutputParser()
        generation = chain.invoke({"context": data, "question": question})

        # 출처 태그 추가
        if category == "code_review":
            generation += "\n(review)"
        elif category == "code_refactor":
            generation += "\n(refactor)"
        elif category == "check_convention":
            generation += "\n(convention)"
        elif category == "generate_test_code":
            generation += "\n(test code)"
        else: generation +="\n(일반)"

        return {
            "question": question,
            "data": data,
            "generation": generation,
            "category": category,
        }

    def _extract_route(self, state: State) -> str:
        """
        라우팅 결과 추출
        """
        return state["generation"]


## TODO : 라우팅 조건 확인
    def route_question(self, state: State):
        """
        질문 라우팅 처리
        """

        route_system_message = (
            "당신은 사용자의 질문에 답변하기 위한 소스를 선택해야 합니다."
        )
        usable_tools_list = ["`plain_answer`"]
        
        route_system_message += f"code refactoring의 내용과 관련된 질문이라면 code_refactor를 활용하세요."
        usable_tools_list.append("`code_refactor`")


        route_system_message += f"code review의 내용과 관련된 질문이라면 code_review를 활용하세요."
        usable_tools_list.append("`code_review`")
        
        
        route_system_message += f"test code의 내용과 관련된 질문이라면 generate_test_code를 활용하세요."
        usable_tools_list.append("`generate_test_code`")
        
        
        route_system_message += f"code convention의 내용과 관련된 질문이라면 check_convention를 활용하세요."
        usable_tools_list.append("`check_convention`")

        route_system_message += "그 외의 질문이라면 plain_answer로 답변합니다.\n"
        usable_tools_text = ", ".join(usable_tools_list)
        route_system_message += (
            f"주어진 질문에 맞춰 {usable_tools_text} 중 하나를 선택하세요.\n"
        )
        route_system_message +=  f"어떤 {usable_tools_text}를 사용했는지 밝히세요\n"
        route_system_message += "답변은 `route` key 하나만 있는 JSON으로 답변하고, 다른 텍스트나 설명을 생성하지 마세요."

        route_prompt = ChatPromptTemplate.from_messages(
            [("system", route_system_message), ("human", "{question}")]
        )

        router_chain = route_prompt | self.route_llm | JsonOutputParser()
        
        question = state["question"]
        route = router_chain.invoke({"question": question})["route"]

        return {
            "question": state["question"],
            "generation": route.lower().strip(),
        }
