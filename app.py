
# this code is used as the module file for the another file where we use these funtion as dataset 
'''
def greeet(name):
    return f"hello{name}"
print(greeet("krish"))
def add(a, b):
    return a + b
input1 = int(input("Enter first number: "))
input2 = int(input("Enter second number: "))
result = add(input1, input2)
print(f"The sum of {input1} and {input2} is: {result}")
'''
# creation of the tool by agentic AI
import os
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.common.exceptions import TimeoutException
from langchain_core.tools import tool
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.agents import initialize_agent, AgentType
# personal details 
LINKEDIN_EMAIL = os.environ.get("LINKEDIN_EMAIL", "2023pietcakrish034@poornima.org")
LINKEDIN_PASSWORD = os.environ.get("LINKEDIN_PASSWORD", "Enter your own password")
IMAGE_PATH = os.path.abspath("Screenshots/Screenshot 2025-07-14 152106.png")
CHROMEDRIVER_PATH = "./chromedriver.exe"
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY", "Enter your own Api key")
# --- Helper Function ---
def sanitize_for_selenium(text: str) -> str:
    """
    Removes non-BMP (Basic Multilingual Plane) characters from a string.
    Some versions of ChromeDriver cannot handle characters like emojis, causing crashes.
    This function ensures the text is safe to be used with Selenium's send_keys.
    """
    return "".join(c for c in text if c <= '\uFFFF')
#setting up the llm model
llm = ChatGoogleGenerativeAI(
    model="gemini-1.5-flash",
    temperature=0.3,
    google_api_key=GOOGLE_API_KEY
)

@tool
def generate_linkedin_post_content(prompt: str) -> str:
    """
    Generates engaging and professional LinkedIn post content based on a user's prompt.
    It should include a main body, relevant hashtags, and a call to action.
    """
    full_prompt = f"""
    Generate a professional and engaging LinkedIn post based on the following topic: '{prompt}'.
    The post should have:
    1. A compelling hook to grab attention.
    2. A main body that provides value or insight.
    3. A concluding sentence or a question to encourage engagement.
    4. 3-5 relevant and popular hashtags.

    Here is the topic:
    {prompt}
    """
    print("Generating post content with LLM...")
    response = llm.invoke(full_prompt)
    return response.content

#  LangChain Agent Setup 
tools = [generate_linkedin_post_content]
agent = initialize_agent(
    llm=llm,
    tools=tools,
    agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
    verbose=True,
    handle_parsing_errors=True
)

#  Main Automation Logic 
def main():
    """Main function to run the LinkedIn automation."""
    user_prompt = input("Enter the topic for your LinkedIn post: ")
    print("\n--- Agent is thinking... ---")
    generated_post = agent.run(user_prompt)
    print("--- Agent finished. ---")
    print("\nGenerated LinkedIn Post:\n" + "="*30)
    print(generated_post)
    print("="*30 + "\n")

    #  CHANGE: Sanitize the post content before sending it to Selenium by removing any kind of emoji or symbol 
    print("Sanitizing post to remove special characters (like emojis)...")
    sanitized_post = sanitize_for_selenium(generated_post)

    #  Selenium Web Automation 
    service = Service(executable_path=CHROMEDRIVER_PATH)
    options = webdriver.ChromeOptions()
    driver = webdriver.Chrome(service=service, options=options)
    driver.maximize_window()
    wait = WebDriverWait(driver, 40)

    try:
        # 1. Login to LinkedIn
        print("Navigating to LinkedIn login page...")
        driver.get("https://www.linkedin.com/login")

        print("Entering credentials...")
        wait.until(EC.presence_of_element_located((By.ID, "username"))).send_keys(LINKEDIN_EMAIL)
        driver.find_element(By.ID, "password").send_keys(LINKEDIN_PASSWORD)
        driver.find_element(By.XPATH, "//button[@type='submit']").click()
        print("Login button clicked.")

        # 2. Initiate Post Creation
        print("Finding 'Start a post' button...")
        start_post_button_selector = "//button[contains(., 'Start a post')]"
        start_post_btn = wait.until(EC.element_to_be_clickable((By.XPATH, start_post_button_selector)))
        start_post_btn.click()
        print("'Start a post' button clicked.")

        # 3. Write the Post
        print("Writing the generated post into the editor...")
        post_editor_selector = "div.ql-editor"
        post_editor = wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, post_editor_selector)))
        # --- CHANGE: Use the sanitized post text ---
        post_editor.send_keys(sanitized_post)
        print("Post text has been entered.")

        # 4. Attach the Image
        print("Attaching the image...")
        add_media_button_selector = "//button[contains(@aria-label, 'Add media')]"
        add_media_button = wait.until(EC.element_to_be_clickable((By.XPATH, add_media_button_selector)))
        add_media_button.click()

        file_input_selector = "input[type='file']"
        file_input = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, file_input_selector)))
        file_input.send_keys(IMAGE_PATH)
        print(f"Image path '{IMAGE_PATH}' sent to file input.")

        done_button_selector = "//span[text()='Done']"
        wait.until(EC.element_to_be_clickable((By.XPATH, done_button_selector))).click()
        print("Image uploaded and 'Done' button clicked.")

        # 5. Publish the Post
        print("Publishing the post...")
        post_button_selector = "button.share-actions__primary-action"
        post_button = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, post_button_selector)))
        post_button.click()

        print(" Post successfully published!")
        time.sleep(5)

    except TimeoutException as e:
        print(f" A timeout occurred. An element was not found in time. Check your selectors or network speed.")
        driver.save_screenshot("linkedin_error.png")
        print("Screenshot saved as 'linkedin_error.png'.")
    except Exception as e:
        print(f" An unexpected error occurred: {e}")
        driver.save_screenshot("linkedin_error.png")
        print("Screenshot saved as 'linkedin_error.png'.")
    finally:
        print("Closing the browser.")
        driver.quit()

if __name__ == "__main__":
    if "your_email" in LINKEDIN_EMAIL or "your_password" in LINKEDIN_PASSWORD or "YOUR_GOOGLE_API_KEY" in GOOGLE_API_KEY:
         print(" CRITICAL: Please update the script with your actual LinkedIn credentials, image path, and Google API key before running.")
    else:
        main()
