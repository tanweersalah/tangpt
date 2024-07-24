<template>
  <main class="home-container">
    <div class="q-pa-m">
      <q-layout
        view="hHh Lpr lff"
        container
        style="height: 100vh"
        class="shadow-2 rounded-borders"
      >
        <q-header elevated class="bg-black">
          <q-toolbar>
            <q-btn flat @click="drawer = !drawer" round dense icon="menu" />
            <q-toolbar-title>TanGPT</q-toolbar-title>
          </q-toolbar>
        </q-header>

        <q-drawer
          v-model="drawer"
          show-if-above
          :width="200"
          :breakpoint="500"
          bordered
          class="bg-grey-9"
        >
          <q-scroll-area class="fit">
            <q-list>
              <template v-for="(menuItem, index) in menuList" :key="index">
                <q-item
                  clickable
                  :active="menuItem.label === 'Outbox'"
                  v-ripple
                >
                  <q-item-section avatar>
                    <q-icon :name="menuItem.icon" />
                  </q-item-section>
                  <q-item-section>
                    {{ menuItem.label }}
                  </q-item-section>
                </q-item>
                <q-separator :key="'sep' + index" v-if="menuItem.separator" />
              </template>
            </q-list>
          </q-scroll-area>
        </q-drawer>

        <q-page-container class="page-content">
          <div class="chat-window">
            <div class="q-pa-md row justify-center">
              <q-scroll-area class="fit" style="width: 100%">
                <q-chat-message
                  name="me"
                  avatar="https://cdn.quasar.dev/img/avatar3.jpg"
                  stamp="7 minutes ago"
                  sent
                  text-color="white"
                  bg-color="primary"
                >
                  <div>Hey there!</div>

                  <div>
                    Have you seen Quasar?
                    <img
                      src="https://cdn.quasar.dev/img/discord-omq.png"
                      class="my-emoticon"
                    />
                  </div>
                </q-chat-message>

                <q-chat-message
                  name="Jane"
                  avatar="https://cdn.quasar.dev/img/avatar5.jpg"
                  bg-color="amber"
                >
                  <q-spinner-dots size="2rem" />
                </q-chat-message>
              </q-scroll-area>
            </div>

            <div class="chat-text-box">
              <q-input
                rounded
                outlined
                dense
                autogrow
                class="chat-input"
                bg-color="grey"
                v-model="message"
                placeholder="Type a message"
              >
                <template v-slot:append>
                  <q-avatar>
                    <img src="https://cdn.quasar.dev/logo-v2/svg/logo.svg" />
                  </q-avatar>
                </template>
              </q-input>
            </div>
          </div>
        </q-page-container>
      </q-layout>
    </div>
  </main>
</template>

<script>
import { ref } from "vue";

const menuList = [
  {
    icon: "inbox",
    label: "Chat History",
    separator: true,
  },
];

export default {
  setup() {
    return {
      drawer: ref(true),
      menuList,
    };
  },
};
</script>

<style scoped>
.page-content {
  height: 100vh;
}
.chat-window {
  display: grid;
  grid-template-rows: 1fr auto;
  height: 100%;
}
.chat-text-box {
  align-self: center;
  padding: 20px;
}
.chat-input {
  width: 100%;
}

.home-container {
  height: 100vh;
  width: 100vw;
}

.chat-history {
  background-color: rgb(38, 56, 50);
}

.chat-container {
  background-color: aquamarine;
}
</style>

<style lang="sass">
.my-emoticon
  vertical-align: middle
  height: 2em
  width: 2em
</style>
