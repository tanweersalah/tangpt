<template>
  <main class="home-container">
    <div class="q-pa-m">
      <q-layout class="shadow-2 rounded-borders">
        <q-header elevated class="bg-black">
          <q-toolbar>
            <q-btn flat @click="drawer = !drawer" round dense icon="menu" />
            <q-toolbar-title>TanGPT</q-toolbar-title>
          </q-toolbar>
        </q-header>

        <q-drawer
          v-model="drawer"
          :width="200"
          :breakpoint="500"
          bordered
          class="bg-grey-9"
        >
          <q-select
            outlined
            dark
            behavior="dialog"
            v-model="selected_model"
            :options="options"
            label="Select Model"
          />
        </q-drawer>

        <q-page-container class="page-content">
          <div class="chat-window">
            <div class="chat-area">
              <q-scroll-area class="fit" ref="chatScroll">
                <div class="welcome-msg" v-if="messages.length === 0">
                  <MessageBox
                    text="Quiz me on ancient civilizations"
                    icon="school"
                    icon_color="blue"
                  />
                  <MessageBox
                    text="Content calendar for TikTok"
                    icon="edit"
                    icon_color="yellow"
                  />
                  <MessageBox
                    text="Activities to make friends in new city"
                    icon="lightbulb"
                    icon_color="orange"
                  />
                  <MessageBox
                    text="Plan a relaxing day"
                    icon="flight"
                    icon_color="green"
                  />
                </div>
                <div v-for="(message, index) in messages" :key="index">
                  <q-chat-message
                    v-if="message['type'] === 'user'"
                    name="me"
                    sent
                    text-color="white"
                    bg-color="primary"
                    class="user-text"
                  >
                    <div>{{ message["message"] }}</div>
                  </q-chat-message>

                  <q-chat-message
                    v-if="message['type'] === 'gpt'"
                    name="TanGPT"
                    text-color="black"
                  >
                    <div v-html="message['message']" />
                    <!-- <q-spinner-dots size="2rem" /> -->
                  </q-chat-message>
                </div>
                <q-chat-message
                  v-if="message_procession"
                  name="TanGPT"
                  avatar="https://geeksgod.com/wp-content/uploads/2021/05/Logopit_1603470318463-300x300.png"
                  bg-color="green"
                >
                  <q-spinner-dots size="2rem" />
                </q-chat-message>
                <q-scroll-observer />
              </q-scroll-area>
            </div>

            <div class="chat-text-box">
              <q-form @submit="onSubmit" @reset="onReset" class="q-gutter-md">
                <q-input
                  rounded
                  outlined
                  standout
                  ref="chatInput"
                  class="chat-input"
                  bg-color="grey"
                  v-model="message"
                  placeholder="Type a message"
                >
                  <template v-slot:append>
                    <q-btn
                      class="send-button"
                      round
                      flat
                      icon="send"
                      color="black"
                      type="submit"
                      @click="get_response()"
                    />
                  </template>
                </q-input>
              </q-form>
            </div>
          </div>
        </q-page-container>
      </q-layout>
    </div>
  </main>
</template>

<script>
import { inject, ref } from "vue";
import { marked } from "marked";
import MessageBox from "../components/MessageBox.vue";
import { useQuasar } from "quasar";

const menuList = [
  {
    icon: "inbox",
    label: "Chat History",
    separator: true,
  },
];

export default {
  setup() {
    const $q = useQuasar();

    return {
      showNotif(msg) {
        $q.notify({
          position: "top",
          message: "Server Error : " + msg,
          color: "red",
        });
      },
    };
  },

  components: { MessageBox },
  mounted() {
    this.focusInput();
  },
  created() {
    var uniqueId = this.generateUniqueId();

    // Store the new unique ID in session storage
    sessionStorage.setItem("uniqueId", uniqueId);

    console.log(uniqueId);
  },
  methods: {
    focusInput() {
      this.$refs.chatInput.focus();
    },
    getUniqueId() {
      // Define the key used to store the unique ID in session storage
      const uniqueIdKey = "uniqueId";

      // Check if the unique ID is already stored in session storage
      let uniqueId = sessionStorage.getItem(uniqueIdKey);

      // If the unique ID does not exist, generate a new one
      if (!uniqueId) {
        // Generate a new unique ID
        uniqueId = this.generateUniqueId();

        // Store the new unique ID in session storage
        sessionStorage.setItem(uniqueIdKey, uniqueId);
      }

      // Return the unique ID
      return uniqueId;
    },

    // Helper function to generate a new unique ID
    generateUniqueId() {
      // You can use any unique ID generation logic here
      // This example uses a combination of the current timestamp and a random number
      return "id-" + Date.now() + "-" + Math.floor(Math.random() * 10000);
    },
    scrollToBottom() {
      const scrollArea = this.$refs.chatScroll;
      if (scrollArea && scrollArea.$el) {
        const scrollElement = scrollArea.$el.querySelector(
          ".q-scrollarea__container"
        );
        if (scrollElement) {
          scrollElement.scrollTop = scrollElement.scrollHeight;
        }
      }
    },

    async get_response() {
      var text = this.message.trim();
      this.message = "";
      if (text !== "") {
        var u_id = this.getUniqueId();
        console.log(u_id);
        this.messages.push({ type: "user", message: text });
        this.message_procession = true;
        setTimeout(() => {
          this.scrollToBottom();
        }, 200);
        console.log(
          this.llms[this.selected_model]["llm"],
          this.llms[this.selected_model]["model_name"]
        );
        try {
          var response = await this.backend.getGptResponse(
            text,
            u_id,
            this.llms[this.selected_model]["llm"],
            this.llms[this.selected_model]["model_name"]
          );

          if (response.status == 200) {
            console.log(response);
            var html_msg = this.renderedMarkdown(response.data["response"]);
            this.messages.push({ type: "gpt", message: html_msg });
            this.message = "";
          }
        } catch (error) {
          // Handle the error
          console.error("Error : ", error);
          this.showNotif(error);
          this.messages.pop();
        }
        this.message_procession = false;
        this.focusInput();
      }
    },
    renderedMarkdown(text) {
      return marked(text);
    },
  },

  data() {
    return {
      options: [
        "llama-3.1-8b-instant",
        "llama-3.1-70b-versatile",
        "gpt-4o-mini",
        "gpt-4o",
        "gpt-4-turbo",
        "gpt-3.5-turbo",
        "gemma2-9b-it",
        "gemma-7b-it",

        "llama3-8b-8192",
      ],
      selected_model: "llama-3.1-8b-instant",
      llms: {
        "llama3-8b-8192": {
          llm: "GROQ",
          model_name: "llama3-8b-8192",
        },
        "llama-3.1-70b-versatile": {
          llm: "GROQ",
          model_name: "llama-3.1-70b-versatile",
        },
        "llama-3.1-8b-instant": {
          llm: "GROQ",
          model_name: "llama-3.1-8b-instant",
        },
        "gemma2-9b-it": {
          llm: "GROQ",
          model_name: "gemma2-9b-it",
        },
        "gemma-7b-it": {
          llm: "GROQ",
          model_name: "gemma-7b-it",
        },
        "gpt-4o-mini": { llm: "OPENAI", model_name: "gpt-4o-mini" },
        "gpt-4o": { llm: "OPENAI", model_name: "gpt-4o" },
        "gpt-4-turbo": { llm: "OPENAI", model_name: "gpt-4-turbo" },
        "gpt-3.5-turbo": { llm: "OPENAI", model_name: "gpt-3.5-turbo" },
      },
      backend: inject("backendService"),

      messages: [],
      message_procession: false,
      scrollsize: 0,
      drawer: false,
    };
  },
};
</script>

<style scoped>
.welcome-msg {
  display: flex;
  flex-wrap: wrap;
  justify-content: center;
  align-content: center;
  gap: 10px;

  height: 70vh;
}
.page-content {
  height: 100dvh;
  width: 100%;
  display: flex;
  justify-content: center;
}
.user-text {
  padding-right: 10px;
}
.chat-area {
  flex-grow: 1;
  margin: 10px;
}
.chat-area .fit {
  width: 100%;
}

.chat-window {
  max-width: 1200px;
  font-size: 1.1rem;
  display: flex;
  flex-direction: column;
  width: 100vw;
}
.chat-text-box {
  align-self: center;
  max-width: 900px;
  width: 100%;
  padding-left: 20px;
  padding-right: 20px;
  padding-bottom: 20px;
}
.chat-input {
  max-height: 300px;
  overflow: auto;
  width: 100%;
}

.home-container {
  height: 100%;
  width: 100vw;
}

.chat-history {
  background-color: rgb(38, 56, 50);
}

.chat-container {
  background-color: aquamarine;
}

img {
  background: antiquewhite !important;
  width: 20px !important;
  height: 20px !important;
  min-width: 20px !important;
}
</style>
