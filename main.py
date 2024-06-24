import streamlit as st
from admin import admin_interface
from player import player_interface

def main():
    player_interface()
    admin_interface()

if __name__ == '__main__':
    main()
