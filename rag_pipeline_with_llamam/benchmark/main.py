import json
import os
from ragas import evaluate, RunConfig
from ragas.metrics import faithfulness, answer_correctness, answer_relevancy, answer_similarity, context_recall

from langchain_community.embeddings import CohereEmbeddings
from langchain_community.llms import Cohere

from src.benchmark import Benchmark


os.environ["COHERE_API_KEY"] = "qOTcu0Xr3BGmpAO8zk9z41y7gx06mO3cgGQOcvlt"

benchmark = Benchmark(
    llm=Cohere(model="command-xlarge"),
    embeddings=CohereEmbeddings(model="embed-multilingual-v3.0"),
    metrics=[faithfulness, answer_correctness, answer_relevancy, answer_similarity, context_recall]
)

benchmark.run(
    groundtruth_filepath="benchmark/test.jsonl",
    result_filepath="benchmark/test_result.jsonl",
    answer_provider=lambda _, __: "The primary cause of global warming is the increase in greenhouse gases, particularly carbon dioxide (CO2) from human activities such as burning fossil fuels.",
    contexts_provider=lambda _: [
        "The Earth’s climate has been undergoing significant changes over the past century, primarily due to the increased concentration of greenhouse gases in the atmosphere. Human activities, such as burning fossil fuels like coal, oil, and natural gas, have released large amounts of carbon dioxide (CO2) and other greenhouse gases into the atmosphere. These gases trap heat from the sun, leading to a gradual rise in the Earth's temperature, a phenomenon known as global warming. Since the Industrial Revolution, CO2 levels have increased dramatically, contributing to more extreme weather events, rising sea levels, and disruptions to ecosystems worldwide.",
        "The primary drivers of climate change include the release of greenhouse gases such as carbon dioxide, methane, and nitrous oxide. These gases trap heat in the atmosphere, which causes the greenhouse effect. The burning of fossil fuels, such as coal, oil, and natural gas, is the largest source of greenhouse gas emissions from human activities in the United States. Globally, deforestation and agricultural practices are also significant contributors to greenhouse gas emissions. The long-term consequences of these emissions include rising global temperatures, changes in precipitation patterns, and more frequent and severe natural disasters.",
        "The greenhouse effect occurs when gases in Earth's atmosphere trap the sun's heat. This process makes Earth much warmer than it would be without an atmosphere. The greenhouse effect is one of the things that makes Earth a comfortable place to live. However, human activities, especially the burning of fossil fuels, have intensified this natural process, resulting in global warming and climate change. Scientists are increasingly concerned that if greenhouse gas emissions continue at the current rate, the world will face dangerous consequences such as rising sea levels, increased frequency of extreme weather events, and significant impacts on biodiversity and human health."
    ]
)

# qa_datas = Benchmark.load_groundtruth("benchmark/thread_p180000-189999.jsonl")

# with open("benchmark/questions.jsonl", "w", encoding="utf-8") as file:
#     for qa in qa_datas:
#         file.write(json.dumps(qa, ensure_ascii=False) + "\n")