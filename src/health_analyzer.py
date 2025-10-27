"""
Module for AI-based analysis of product health information using Groq.
"""
import os
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from langchain_groq import ChatGroq


class HealthAnalyzer:
    def __init__(self):
        """
        Initialize the health analyzer using GROQ_API_KEY from environment variables.
        """
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            raise ValueError("GROQ_API_KEY environment variable is not set")
            
        # Configure Groq LLM
        self.llm = ChatGroq(
            model="llama-3.3-70b-versatile",
            temperature=0.7,
            max_tokens=512,
            api_key=api_key
        )
        
        # Create prompt template
        self.prompt = PromptTemplate(
            input_variables=["product_info"],
            template="""Analyze the health implications of this food product and provide a detailed response.
            
            Product information: {product_info}
            
            Respond in the following format:
            
            HEALTH RATING:
            - Rate from 1-10 (1 being least healthy, 10 being most healthy)
            
            NUTRITIONAL BENEFITS:
            - List key nutritional benefits
            
            HEALTH CONCERNS:
            - List potential health concerns
            
            DIETARY CONSIDERATIONS:
            - List dietary considerations (e.g., vegan, contains gluten)
            
            RECOMMENDATIONS:
            - Provide specific consumption recommendations
            """
        )
        
        # Create chain
        self.chain = (
            {"product_info": RunnablePassthrough()} 
            | self.prompt 
            | self.llm 
            | StrOutputParser()
        )


    def analyze_product(self, product_info):
        """
        Analyze product information and generate health insights.
        
        Args:
            product_info (dict): Product information from Open Food Facts
            
        Returns:
            str: AI-generated health analysis
        """
        # Convert product info to string format and invoke the chain
        return self.chain.invoke(str(product_info))